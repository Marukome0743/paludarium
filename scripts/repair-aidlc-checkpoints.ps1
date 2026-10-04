param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$old = @'
          auditBlockField(review.block, "Unit Source Fingerprint") !== source ||
'@
$replacement = @'
          // freshReviewReceipts already authenticates the source binding and
          // applies strict invalidation, relaxed drift and newer-unit shielding.
          // Requiring the old hash here would override that authoritative result.
'@
$changes = @(
    @('  freshReviewReceipts,', "  freshReviewReceipts,`n  recordAcceptedChanges,`n  governedGuardPolicy,`n  type AcceptedChange,"),
    @('  command_authorized: boolean;', "  command_authorized: boolean;`n  change_notices?: string[];"),
    @('interface Snapshot {', "interface Snapshot {`n  acceptedChanges: AcceptedChange[];"),
    @('  const evidence: unknown[] = [];', "  const evidence: unknown[] = [];`n  const acceptedChanges: AcceptedChange[] = [];"),
    @('      review = onlyLatest(rows.filter((row) =>', "      acceptedChanges.push(...receipts.acceptedChanges.filter(change => change.unit === unit));`n      review = onlyLatest(rows.filter((row) =>"),
    @('    root, rows, state, verificationCommand: shared.verificationCommand,', '    root, rows, state, acceptedChanges, verificationCommand: shared.verificationCommand,'),
    @('    const proof: ConstructionCheckpointProof = {', "    // Record governed drift once before running the current verification.`n    if (current.acceptedChanges.length > 0) governedGuardPolicy(projectDir, current.state);`n    const changeNotices = recordAcceptedChanges(projectDir, current.acceptedChanges);`n    const proof: ConstructionCheckpointProof = {"),
    @('    return { ...current, proof, command: authorization.command, intent: selection.intent!, space: selection.space };', '    return { ...current, proof, changeNotices, command: authorization.command, intent: selection.intent!, space: selection.space };'),
    @("    return resolveConstructionCheckpoint(projectDir, unit, kind);`n  }, before.intent, before.space);", "    return { ...resolveConstructionCheckpoint(projectDir, unit, kind),`n      ...(before.changeNotices.length > 0 ? { change_notices: before.changeNotices } : {}) };`n  }, before.intent, before.space);" )
)
foreach ($harness in @('.codex', '.claude')) {
    $path = Join-Path $ProjectRoot "$harness/tools/aidlc-construction-checkpoints.ts"
    if (!(Test-Path -LiteralPath $path)) { continue }
    $text = [IO.File]::ReadAllText($path).Replace("`r`n", "`n")
    if (!$text.Contains($replacement)) {
        if ([regex]::Matches($text, [regex]::Escape($old)).Count -ne 1) {
            throw "Unexpected checkpoint source in $path; refusing to patch."
        }
        $text = $text.Replace($old, $replacement)
    }
    foreach ($change in $changes) {
        if ($text.Contains($change[1])) { continue }
        if ([regex]::Matches($text, [regex]::Escape($change[0])).Count -ne 1) {
            throw "Unexpected checkpoint source for '$($change[0])' in $path; refusing to patch."
        }
        $text = $text.Replace($change[0], $change[1])
    }
    [IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))
    Write-Output "$harness`: repaired source comparison and accepted-change recording"

    # SCM metadata is not application source. jj updates it even on status.
    $libPath = Join-Path $ProjectRoot "$harness/tools/aidlc-lib.ts"
    $libText = [IO.File]::ReadAllText($libPath).Replace("`r`n", "`n")
    $sourceNames = 'const SOURCE_FINGERPRINT_HARD_EXCLUDED_NAMES = ['
    $blockStart = $libText.IndexOf($sourceNames, [StringComparison]::Ordinal)
    $blockEnd = $libText.IndexOf('] as const;', $blockStart, [StringComparison]::Ordinal)
    if ($blockStart -lt 0 -or $blockEnd -lt 0) { throw "Unexpected source exclusions in $libPath" }
    $block = $libText.Substring($blockStart, $blockEnd - $blockStart)
    if (!$block.Contains('  ".jj",')) {
        if ([regex]::Matches($block, [regex]::Escape('  ".git",')).Count -ne 1) {
            throw "Unexpected SCM source exclusions in $libPath"
        }
        $newBlock = $block.Replace('  ".git",', "  `".git`",`n  `".jj`",")
        $libText = $libText.Remove($blockStart, $block.Length).Insert($blockStart, $newBlock)
        [IO.File]::WriteAllText($libPath, $libText, [Text.UTF8Encoding]::new($false))
    }
    Write-Output "$harness`: excluded jj internal data from source identity"
}
