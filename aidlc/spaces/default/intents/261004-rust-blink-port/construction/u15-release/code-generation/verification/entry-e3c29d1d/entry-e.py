"""U15 verification entry rooted at e3c29d1d, version e (the person's decision of 2026-10-18).

The person chose option A: "A で進めてください。各 commit の tree のハッシュで照らし合わせる
入口の版 e を作り、独立レビューの後に採用を伺ってください。" Version d (entry-d.py) needed
GitHub's compare file list, which GitHub cuts at 300 files; a head after the local
aidlc/-only commit a7aecb72 (741 files) can never pass it. Version e keeps every
check of version d and replaces only how lineage and changed files are tied to
GitHub:

  E1  lineage: a stored record of every commit of the chain (copied fields of
      GET repos/Marukome0743/paludarium/commits/<sha>: sha, parents[].sha,
      commit.tree.sha, commit.verification.verified/reason) must cover exactly
      the chain; each commit must be Verified, its tree must equal local
      `git rev-parse <sha>^{tree}` and its parents must equal local git's
      parents (and the previous commit of the chain). Equal tree hashes mean
      GitHub and local git hold the same content for every path.
  E2  changed files are counted from local git only
      (`git diff-tree -r --no-renames <base> <head>`): the paths outside aidlc/
      must equal the binding's list exactly (kept as a human-readable list);
      for aidlc/ the binding gives the count and the SHA-256 of the sorted
      list, and both must match.
  E3  the GitHub compare response is not used at all (neither its file list
      nor its status); lineage comes from E1 and local `git rev-list`.

Every other check of version d stays: (0) base records and history, (3) the
working copy (all tracked bytes, exclusions), (4) CI (7 required workflows,
job sets, at most 2 reruns), (5) performance (FR8.3, artifact expired /
repository_id), (6) upstream, git without user/system configuration.

Command line: `--entry-sha256 <hex> --binding-sha256 <hex>`, in this order.
The binding is the one binding-e*.json in this folder with that SHA-256.
Argument or pin mismatch: exit 2 before any check, nothing written. A refused
check: exit 1 and refusal.json; a pass: exit 0 and result.json, both in a
fresh run-<ns>-<pid>/ folder created exclusively.

Only read-only local git (rev-parse, rev-list, ls-tree, diff-tree, cat-file,
check-ignore) is used. No network, GitHub query, build, CI, measurement or
publish.
"""
import hashlib,io,json,os,re,subprocess,sys,time,traceback,zipfile
from pathlib import Path

OWN=Path(__file__).resolve().parent
SELF=Path(__file__).resolve()
ROOT=next(p for p in OWN.parents if (p/'Cargo.toml').is_file())
INTENT='aidlc/spaces/default/intents/261004-rust-blink-port/'
U15V=INTENT+'construction/u15-release/code-generation/verification/'
LOOP=U15V+'version-allowance/'
HERE=U15V+'entry-e3c29d1d/'
REPOSITORY='Marukome0743/paludarium'
# The fork's numeric repository id (read once with a read-only `gh api repos/Marukome0743/paludarium` GET on 2026-10-18).
REPOSITORY_ID=1408718913
UPSTREAM_REPOSITORY='aletheia-works/paludarium'
SCHEMA='u15-entry-e3c29d1d-binding/e1'
BASE='e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9'
BASE_TREE='6d6e3995e3e2f9c3a246beb291b9b516cc3a3dcb'
# At most this many runs of one binding may be allowed an attempt 2 (each for one named job; review 02).
MAX_RERUNS=2
PERF_ZIP=U15V+'ci-e3c29d1d/u14-quality-39114108809/artifact-zip/u11-node-12131882922.zip'
PERF_ORIGINAL=U15V+'ci-e3c29d1d/u14-quality-39114108809/u11-node/performance/observations.json'
BASE_ARTIFACTS=HERE+'ci-artifacts-e3c29d1d.json'
BASE_RECORDS={
    'checkpoint':{'copy':HERE+'base-checkpoint-435bc5e0.json','copy_sha256':'b304628676add2c0f5f5603db279b2ad1e3acbe602bbed8068deeb898be10b06',
        'live':INTENT+'.aidlc-construction-checkpoints/u15-release/unit.json','id':'435bc5e0-3818-4691-9d84-a9add39239d9',
        'command_sha256':'aee42ab19c563721540d17e5cb318aebdfdeaf5515083cb3d4872c4b7ac1b48c',
        'entry':LOOP+'u15_candidate_v4.py','entry_sha256':'dfb0e03ae09c51ee3454c367dc7c1f072e6e1428f75f97a371555bb2143df5d0',
        'binding':LOOP+'binding-11.json','binding_sha256':'fb466da7e8f7dadff7efb3645ee5e4f4a95c0eb867207be875387879cf6caca4',
        'result':LOOP+'run-1792320136065939000-60394/result.json','result_sha256':'43b87277e4c273671fabc4fd001f820d6b17850adb199a92f0ceb0e1a348a5d6'},
    'files':{LOOP+'ci-e3c29d1d.json':'7f03c90352b2e926c4beb4764818d7c880844f4cdc433f6b7e0821d86be09eeb',
        LOOP+'ci-jobs-e3c29d1d.json':'93380dd27715de3ec3f1f4720b0615a1d7e965bfecb9c034992755d0cdc522d1',
        BASE_ARTIFACTS:'5f0ea0815149c918feae5ae0ad330f5f645a41807f5a7ba53cd51be637cf62c5',
        PERF_ORIGINAL:'1abc62ff35bcffd3167e6a7de968abcb40ada4a7f5b8afdef4eb66646e03ff45',
        PERF_ZIP:'606c3323f7ab72a8e070584ef20c8c78a515ef2a2d0b55fcf09b8da06b949415'}}
BASE_JOBS=LOOP+'ci-jobs-e3c29d1d.json'
# History, never executed here: v1-v4 entries, binding-08..11 and their regressions, and the earlier
# versions of this entry (entry.py, entry-b.py, entry-c.py, entry-d.py, binding-e01..e04 and their regressions).
HISTORY={LOOP+'u15_candidate.py':'6a5077aef1034f6276c2806c66d0cfb62550812ee95217de92f7c7931b638cc0',
    LOOP+'u15_candidate_v2.py':'b78f867e4baf0a2ccae6f0b6daf4751383069db7913f58fc78a6375b63183ed5',
    LOOP+'u15_candidate_v3.py':'ebb6789417b48d7e8e8ef3c5ae8919483a85eda0ea85ecda5fbf001d74c2e798',
    LOOP+'u15_candidate_v4.py':'dfb0e03ae09c51ee3454c367dc7c1f072e6e1428f75f97a371555bb2143df5d0',
    LOOP+'binding-08.json':'f20954e14dc761f4dc0172d775af3c2602f8f2887539c900fa2319ba33b30262',
    LOOP+'binding-09.json':'687fee0c4a25147aab064ff101b742a8145d5cb46ea608295146745a524e3649',
    LOOP+'binding-10.json':'44f7c2a9ef02e7ebcd83ac4b8a5a639e9628f662187468816d3285001631ee3e',
    LOOP+'binding-11.json':'fb466da7e8f7dadff7efb3645ee5e4f4a95c0eb867207be875387879cf6caca4',
    LOOP+'test_u15_candidate.py':'6573bc6c158199bd1466aa076bdee307e9d82da7503a6cb3d48403572f37e10a',
    LOOP+'test_u15_candidate_v2.py':'57c0727fbfe71716fbd386227292f8d69171d7b5e7ac499f5e277c188fd53b7f',
    LOOP+'test_u15_candidate_v3.py':'148960fa85fcc8074bc833e4c9d9aa086431b993b6990781cdb5b60fe970b068',
    LOOP+'test_u15_candidate_v4.py':'4a225e0a72b00bf05a500853e76a93dff6ad101a6c15e061b31e909f70682bd4',
    HERE+'entry.py':'10472d80f4cc5e4422469cb9d0e10f19ddebe64562ad0a0c33d9d50a98dfc961',
    HERE+'entry-b.py':'95dcedc719224b5a1355266304dab1368a1b03c0f1f0016f95c64095792c1ff6',
    HERE+'entry-c.py':'44a8d9d0388db18fb5730dd54e5bb40f178a309536f39b48dde90d1f5eaf1a5a',
    HERE+'entry-d.py':'7c73492e0b269770bfdea0a63b8f1bd3d87a44b47bc9d091268b375b69e4fac2',
    HERE+'binding-e01.json':'670294220a09c34f23e3c4472db4b61876159573e41abbf0b48afe2f38a6b74b',
    HERE+'binding-e02.json':'66c54627be2abf6fb76588a47416bbfeb4f0acaa7ced191bdff3902b6ee27e02',
    HERE+'binding-e03.json':'fd55262c37b6a50f71c58a677786a8af9aa7469defb3910853da64eadcbbf316',
    HERE+'binding-e04.json':'0fca5fc33f62f9a36262c3ee562b7f61ef31c49cb29ebddeb4d76aaecc8e1981',
    HERE+'test_entry.py':'422e9e5f022acf4320fb143d89dd5f676a92fbe84a9c0d3a16c4cf3d0a316b17',
    HERE+'test_entry_b.py':'67f55f175a7b5fda936a4fcd4de1d7aad7b46690e42c84c328c15c0f86ab97e8',
    HERE+'test_entry_c.py':'371e87e56200cb23444a512627e468825b341cc1f6e012fd80848cc56f82e8b4',
    HERE+'test_entry_d.py':'5548a3b0df1b662d19148f8e5ac24b450ef3955cac0a645b2044cdd6861d916b'}
# The 7 workflows of e3c29d1d: a binding may add workflows, never remove these (review 01, M2).
REQUIRED_WORKFLOWS=('CI','Release package checks','U1 U14 current-source evidence','U12 current full quality','U13 current full quality',
    'U14 current full quality','U14 fresh thirteen target ASan and LSan')
PERF_WORKFLOW='U14 current full quality'
DECISION_B=('2026-10-18 人の判断（選んだ選択肢「git の無視＋2 つ」）：「git が無視するファイル（.gitignore、git check-ignore で読み取りだけ）を除外にし、'
    '.aidlc-version（bytes の違いを許す）と .venv-u15/ を除外の一覧に足す。入口と binding は新しい版（entry-b.py・binding-e02.json）で作り直す」')
REVIEW_C='2026-10-18 独立レビュー independent-review-01.md（NOT-READY、Major 3）への対応で版 c（entry-c.py・binding-e03.json）を作った。git の無視は head の tree にある .gitignore の規則だけ、bytes の違いを許す追跡ファイルは .aidlc-version と mise.toml だけ。'
DECISION_E=('2026-10-18 人の判断（原文）：「A で進めてください。各 commit の tree のハッシュで照らし合わせる入口の版 e を作り、独立レビューの後に採用を伺ってください。'
    '記録と製品は一緒に 1 回で push します。」')
REVIEW_E=('版 e（entry-e.py）：版 d の検査をすべて残し、GitHub の compare（300 件の上限）を使わず、保存した各 commit の記録の tree のハッシュ・親・署名を手元の git と照合する。'
    '変わったファイルは手元の git だけで数え、aidlc/ の外は binding の一覧、aidlc/ の中は件数と並べた一覧の SHA-256 と一致を求める。除外の一覧は版 c と同じ。')
GIT_IGNORE_COMMAND='git -c core.excludesFile= check-ignore -z -v -n --no-index --stdin（GIT_* の環境変数なし）'
# The exclusion list is the same as in version c (the person's decision and review 01); version e does not change it.
EXCLUSIONS={'decision':DECISION_B,'decided':'2026-10-18','review':REVIEW_C,
    'top_level':['.git','.jj','.venv-u15','aidlc'],'directory_components':['__pycache__','node_modules','target'],
    'file_names':['.DS_Store'],'paths_bytes_may_differ':['.aidlc-version','mise.toml'],'prefixes':['tools/aidlc-recovery/'],
    'by_name_applies_to':'head の tree に無いパスだけ。head の tree にある追跡ファイルは、paths_bytes_may_differ の 2 つを除き必ず bytes を比べる / only paths not in the head tree; tracked head files are always compared except the 2 paths_bytes_may_differ',
    'git_ignored_untracked':{'enabled':True,'command':GIT_IGNORE_COMMAND,
        'accepted_sources':'head の tree にある .gitignore だけ（.git/info/exclude・core.excludesFile・未追跡の .gitignore は認めない） / only .gitignore files in the head tree',
        'applies_to':'head の tree に無いパスだけ / only paths not in the head tree'}}
DIR_NOTE='未追跡の中身だけ。中の追跡ファイルは比べる / untracked contents only; tracked files inside are compared'
TOP_LEVEL_NOTES={'aidlc':'aidlc/ の中は比べない（head の tree の aidlc/ は最初から比べる対象の外） / not compared: aidlc/ is outside the compared tree',
    '.git':'git の内部。追跡ファイルを持たない / git internals; holds no tracked files',
    '.jj':'jj の内部。追跡ファイルを持たない / jj internals; holds no tracked files'}
BINDING_KEYS={'schema','purpose','approval','repository','base','base_records','history','head','commit_chain','commit_records','changed_files',
    'aidlc_changed','exclusions','ci','ci_jobs','ci_artifacts','performance','upstream'}
USAGE='usage: entry-e.py --entry-sha256 <64 hex> --binding-sha256 <64 hex>'
HEX40=re.compile(r'[0-9a-f]{40}');HEX64=re.compile(r'[0-9a-f]{64}')
GIT_READ_ONLY={'rev-parse','rev-list','ls-tree','diff-tree','cat-file','check-ignore'}
GIT_ARGS=('git','--no-optional-locks','-c','core.quotepath=off','-c','core.excludesFile=','-c','core.fsmonitor=false')
sha=lambda b:hashlib.sha256(b).hexdigest()
# Regression-only in-memory overlay {repo-relative path: bytes, or None for "absent"; a key ending in "/"
# with None shows a directory as absent}. None in real runs.
OVERLAY=None
OUT_DIR=OWN

class Refusal(ValueError):
    def __init__(self,message,details=None):
        super().__init__(message);self.details=details or {}

def need(value,message):
    if not value:raise Refusal(message)

def in_aidlc(rel):return rel.split('/',1)[0]=='aidlc'

def read(rel):
    """Bytes of a repo-relative file (no symlink), honouring the regression overlay."""
    if OVERLAY is not None and rel in OVERLAY:
        if OVERLAY[rel] is None:raise Refusal('file missing: '+rel)
        return OVERLAY[rel]
    path=ROOT/rel
    need(not path.is_symlink(),'symlinked file: '+rel)
    try:return path.read_bytes()
    except OSError as error:raise Refusal('file missing: '+rel) from error

def pinned(rel,pin,what):
    need(sha(read(rel))==pin,what+' bytes differ from the pinned SHA-256: '+rel)

def strict_json(raw,what):
    def pairs(items):
        keys=[k for k,_ in items];need(len(keys)==len(set(keys)),'duplicate key in '+what);return dict(items)
    try:return json.loads(raw,object_pairs_hook=pairs)
    except (UnicodeDecodeError,json.JSONDecodeError) as error:raise Refusal('not JSON: '+what) from error

def git_env():
    """The environment without any GIT_* variable, and with no global or system git configuration (review 02)."""
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_OPTIONAL_LOCKS='0',GIT_TERMINAL_PROMPT='0',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull)
    return env

def git(*args,stdin=None,ok=(0,)):
    """Read-only local git; never writes the repository (no optional locks)."""
    need(args and args[0] in GIT_READ_ONLY,'git command outside the read-only set')
    r=subprocess.run([*GIT_ARGS,*args],cwd=ROOT,input=stdin,capture_output=True,timeout=300,env=git_env())
    need(r.returncode in ok,'git '+' '.join(args[:3])+' failed: '+r.stderr.decode('utf-8','replace').strip()[:300])
    return r.stdout

def git_tree(commit):return git('rev-parse','--verify',commit+'^{tree}').decode().strip()
def git_parents(commit):
    out=git('rev-list','--parents','-n','1',commit).decode().split()
    need(out and out[0]==commit,'local git does not know the commit: '+commit)
    return out[1:]
def git_has_commit(commit):
    r=subprocess.run([*GIT_ARGS,'cat-file','-e',commit+'^{commit}'],cwd=ROOT,capture_output=True,timeout=60,env=git_env())
    return r.returncode==0

def head_tree(head):
    """{path: (mode, blob id)} of every entry of head's tree outside aidlc/."""
    out={}
    for row in git('ls-tree','-r','-z','--full-tree',head).split(b'\0'):
        if not row:continue
        meta,path=row.split(b'\t',1);mode,kind,oid=meta.decode().split(' ');p=path.decode('utf-8')
        if in_aidlc(p):continue
        need(kind=='blob' and mode in ('100644','100755','120000'),'unsupported tree entry (submodule or other): '+p)
        out[p]=(mode,oid)
    return out

def blobs(oids):
    """Contents of blob ids through one read-only cat-file --batch."""
    if not oids:return {}
    raw=git('cat-file','--batch',stdin=''.join(o+'\n' for o in oids).encode());out={};i=0
    for o in oids:
        nl=raw.index(b'\n',i);header=raw[i:nl].decode().split(' ')
        need(len(header)==3 and header[0]==o and header[1]=='blob','git blob missing: '+o)
        size=int(header[2]);out[o]=raw[nl+1:nl+1+size];i=nl+2+size
    return out

# ---- exclusions -------------------------------------------------------------
def excluded_rule(rel,is_dir,ex):
    """The by-name exclusion rule a path hits, or None (used only for paths not in the head tree)."""
    parts=rel.split('/')
    if parts[0] in ex['top_level']:return 'top_level:'+parts[0]
    dirs=parts if is_dir else parts[:-1]
    for c in dirs:
        if c in ex['directory_components']:return 'directory_component:'+c
    if not is_dir and parts[-1] in ex['file_names']:return 'file_name:'+parts[-1]
    if not is_dir and rel in ex['paths_bytes_may_differ']:return 'path_bytes_may_differ:'+rel
    for pre in ex['prefixes']:
        if (rel+'/' if is_dir else rel).startswith(pre):return 'prefix:'+pre
    return None

def dir_note(rule):
    """The note of a by-name excluded directory row: aidlc/ is not compared, .git/ and .jj/ hold no tracked files."""
    if rule.startswith('top_level:'):return TOP_LEVEL_NOTES.get(rule.split(':',1)[1],DIR_NOTE)
    return DIR_NOTE

def parse_check_ignore(raw,paths,sources):
    """{path: 'source:line:pattern' when a .gitignore in `sources` ignores it, else None} from `git check-ignore -z -v -n` output.
    A rule from any other source (.git/info/exclude, core.excludesFile, an untracked .gitignore) does not count."""
    fields=raw.split(b'\0')
    if fields and fields[-1]==b'':fields.pop()
    need(len(fields)%4==0,'git check-ignore output is malformed')
    out={};foreign={}
    for i in range(0,len(fields),4):
        source,line,pattern,path=(f.decode('utf-8') for f in fields[i:i+4])
        ignored=bool(source) and not pattern.startswith('!')
        if ignored and source not in sources:foreign[path]=source+':'+line+':'+pattern;ignored=False
        out[path]=source+':'+line+':'+pattern if ignored else None
    need(set(out)==set(paths),'git check-ignore did not answer for every path')
    return out,foreign

def git_ignore_status(paths,sources):
    """Read-only: which of these untracked paths a head-tree .gitignore ignores (directories end with /)."""
    if not paths:return {},{}
    for p in paths:need('\0' not in p,'path with a NUL byte: '+repr(p))
    raw=git('check-ignore','-z','-v','-n','--no-index','--stdin',stdin=b''.join(p.encode('utf-8')+b'\0' for p in paths),ok=(0,1))
    return parse_check_ignore(raw,paths,sources)

def walk_working_copy(ex,tree,tree_dirs):
    """(untracked files, by-name excluded dirs, untracked dirs); excluded and untracked directories are not entered."""
    files=[];ex_dirs=[];untracked_dirs=[]
    for dirpath,dirnames,filenames in os.walk(ROOT,topdown=True,followlinks=False):
        base=Path(dirpath).relative_to(ROOT).as_posix();base='' if base=='.' else base+'/'
        keep=[]
        for d in sorted(dirnames):
            rel=base+d
            if OVERLAY and OVERLAY.get(rel+'/',b'') is None:continue  # regression-only: directory shown as absent
            if (ROOT/rel).is_symlink():files.append(rel);continue
            rule=excluded_rule(rel,True,ex)
            if rule and rule.startswith('prefix:'):keep.append(d)  # the person's prefix: entered, each file listed
            elif rule:ex_dirs.append(dict(path=rel+'/',kind='directory',rule=rule,note=dir_note(rule)))
            elif rel not in tree_dirs:untracked_dirs.append(rel+'/')
            else:keep.append(d)
        dirnames[:]=keep
        files.extend(base+f for f in filenames)
    if OVERLAY:
        files={*files,*(p for p,v in OVERLAY.items() if v is not None and not in_aidlc(p) and not p.endswith('/'))}-{p for p,v in OVERLAY.items() if v is None}
    return sorted(p for p in files if p not in tree),ex_dirs,untracked_dirs

def working_bytes(rel):
    """('file'|'symlink', bytes) of a working-copy path, honouring the overlay."""
    if OVERLAY is not None and rel in OVERLAY:
        if OVERLAY[rel] is None:return None,None
        return 'file',OVERLAY[rel]
    path=ROOT/rel
    try:
        if path.is_symlink():return 'symlink',os.readlink(path).encode()
        return 'file',path.read_bytes()
    except OSError:return None,None

def verify_working_copy(head,ex):
    """(3) every file of head's tree outside aidlc/ equals head's blob (only .aidlc-version and mise.toml may differ);
    any other path is excluded by name or ignored by a head-tree .gitignore."""
    tree=head_tree(head);tree_dirs={'/'.join(p.split('/')[:i]) for p in tree for i in range(1,p.count('/')+1)}
    content=blobs(sorted({oid for _,oid in tree.values()}))
    differing=[];missing=[];kind_mismatch=[];by_name=[];compared=0
    for rel,(mode,oid) in sorted(tree.items()):
        kind,data=working_bytes(rel)
        if kind is None:missing.append(rel);continue
        if (kind=='symlink')!=(mode=='120000'):kind_mismatch.append(rel);continue
        if rel in ex['paths_bytes_may_differ']:
            by_name.append(dict(path=rel,kind='file',rule='path_bytes_may_differ:'+rel,in_head_tree=True,bytes_equal_head=data==content[oid]));continue
        compared+=1
        if data!=content[oid]:differing.append(rel)
    files,ex_dirs,untracked_dirs=walk_working_copy(ex,tree,tree_dirs);by_name.extend(ex_dirs);candidates=list(untracked_dirs)
    for rel in files:
        rule=excluded_rule(rel,False,ex)
        if rule:by_name.append(dict(path=rel,kind='file',rule=rule,in_head_tree=False))
        else:candidates.append(rel)
    need(not set(candidates)&set(tree),'internal: a head path reached the git ignore check')
    sources={p for p in tree if p.split('/')[-1]=='.gitignore'}
    status,foreign=git_ignore_status(sorted(candidates),sources) if ex['git_ignored_untracked']['enabled'] else ({},{})
    by_git=[dict(path=p,kind='directory' if p.endswith('/') else 'file',rule='git_ignore',pattern=status[p]) for p in sorted(candidates) if status.get(p)]
    unexpected=[p for p in sorted(candidates) if not status.get(p)]
    problems=dict(differing=sorted(differing),missing=sorted(missing),kind_mismatch=sorted(kind_mismatch),unexpected=unexpected)
    key=lambda r:r['path']
    extra=dict(excluded_by_name=sorted(by_name,key=key),excluded_by_git_ignore=by_git,ignored_by_a_source_not_accepted=dict(sorted(foreign.items())))
    if any(problems.values()):
        listed='; '.join(k+': '+', '.join(v[:8])+(' ...' if len(v)>8 else '') for k,v in problems.items() if v)
        raise Refusal('working copy differs from head '+head+' outside aidlc/ ('+listed+')',dict(problems,**extra))
    return dict(head_tree_files_outside_aidlc=len(tree),compared_equal=compared,accepted_gitignore_sources=sorted(sources),**extra)

# ---- binding, base records, history ----------------------------------------
def check_binding_shape(b):
    need(isinstance(b,dict) and set(b)==BINDING_KEYS,'binding key set differs')
    need(b['schema']==SCHEMA and b['repository']==REPOSITORY,'binding schema/repository differs')
    need(all(isinstance(b[k],str) and b[k].strip() for k in ('purpose','approval')),'binding purpose/approval missing')
    need(b['base']=={'commit':BASE,'tree':BASE_TREE},'binding base differs from e3c29d1d')
    need(b['base_records']==BASE_RECORDS,'binding base records differ from the pinned base records')
    need(b['history']==HISTORY,'binding history pins differ from the pinned history')
    need(b['exclusions']==EXCLUSIONS,'binding exclusion list differs from the approved list')
    need(isinstance(b['head'],str) and HEX40.fullmatch(b['head']) is not None,'binding head is not a commit id')

def verify_history():
    for rel,pin in sorted(HISTORY.items()):pinned(rel,pin,'history file')
    return dict(sorted(HISTORY.items()))

def verify_base_records():
    """(0) the v4 exit-0 checkpoint record at e3c29d1d, its result.json, the stored e3c29d1d CI and the FR8.3 original."""
    c=BASE_RECORDS['checkpoint']
    raw=read(c['copy']);need(sha(raw)==c['copy_sha256'],'base checkpoint record bytes differ from the pinned SHA-256')
    rec=strict_json(raw,'base checkpoint record')
    need(rec.get('id')==c['id'] and rec.get('unit')=='u15-release' and rec.get('kind')=='unit','base checkpoint record id differs')
    need(rec.get('exit_code')==0 and rec.get('signal') is None and rec.get('error') is None and rec.get('verified') is True and rec.get('evidence_unchanged') is True,'base checkpoint verification did not pass')
    need(sha(rec['command_label'].encode())==rec['command_sha256']==c['command_sha256'],'base checkpoint command SHA-256 differs')
    out=rec['stdout_tail'].encode();need(sha(out)==rec['stdout_sha256'] and len(out)==rec['stdout_bytes'],'base checkpoint stdout is not the whole recorded stdout')
    m=re.fullmatch(r'\S+/python3 -B '+re.escape(c['entry'])+r' --entry-sha256 ([0-9a-f]{64}) --binding-sha256 ([0-9a-f]{64})',rec['command_label'])
    need(m is not None and m.group(1)==c['entry_sha256']==HISTORY[c['entry']] and m.group(2)==c['binding_sha256']==HISTORY[c['binding']],'base checkpoint command is not entry v4 with binding-11')
    run_dir=c['result'].rsplit('/',1)[0]
    last=strict_json(rec['stdout_tail'].strip().split('\n')[-1],'base checkpoint stdout')
    need(last.get('output')==run_dir and last.get('u15_candidate_v4')=='PASS','base checkpoint output folder differs')
    raw=read(c['result']);need(sha(raw)==c['result_sha256'],'base result.json bytes differ from the pinned SHA-256')
    res=strict_json(raw,'base result.json')
    need(res.get('u15_candidate_v4')=='PASS' and res.get('entry_sha256')==c['entry_sha256'] and res.get('binding_sha256')==c['binding_sha256'],'base result.json is not the v4 pass')
    for rel,pin in sorted(BASE_RECORDS['files'].items()):pinned(rel,pin,'base record')
    try:live=read(c['live'])
    except Refusal:live=None
    if live is None:live_state='missing (the pinned copy is used)'
    elif sha(live)==c['copy_sha256']:live_state='equal to the pinned copy'
    else:
        lid=strict_json(live,'live checkpoint record').get('id')
        need(isinstance(lid,str) and lid.strip(),'live checkpoint record has no id')
        need(lid!=c['id'],'live checkpoint record has the base id but different bytes')
        live_state='superseded by a later checkpoint record (id '+lid+'); the pinned copy is used'
    return dict(checkpoint_id=c['id'],command_sha256=c['command_sha256'],started_at=rec['started_at'],finished_at=rec['finished_at'],
        entry_v4_sha256=c['entry_sha256'],binding_11_sha256=c['binding_sha256'],result=c['result'],result_sha256=c['result_sha256'],
        live_checkpoint_record=live_state,files=dict(sorted(BASE_RECORDS['files'].items())))

# ---- (1) lineage by commit records (E1), (2) changed files by local git (E2) ----
def field(record,*keys):
    for k in keys:
        record=record.get(k) if isinstance(record,dict) else None
    return record

def verify_lineage(spec,chain,base,head):
    """(1) the stored commit records cover exactly the chain; every commit is Verified, its tree equals the local tree
    and its parents equal local git's parents (and the previous commit of the chain)."""
    need(isinstance(chain,list) and chain and all(isinstance(c,str) and HEX40.fullmatch(c) for c in chain) and len(set(chain))==len(chain),'commit chain differs')
    need(chain[0]==base and chain[-1]==head,'commit chain does not run from the base to the head')
    need(isinstance(spec,dict) and set(spec)=={'path','sha256'},'commit records binding key set differs')
    pinned(spec['path'],spec['sha256'],'commit records')
    doc=strict_json(read(spec['path']),'commit records')
    need(isinstance(doc,dict) and doc.get('repository')==REPOSITORY and isinstance(doc.get('commits'),list),'commit records repository differs')
    shas=[field(r,'sha') for r in doc['commits']]
    need(len(shas)==len(set(shas)),'commit records list a commit twice')
    need(set(shas)==set(chain),'commit records do not cover exactly the chain: missing '+', '.join(sorted(set(chain)-set(shas)))+'; extra '+', '.join(sorted(str(s) for s in set(shas)-set(chain))))
    by_sha={r['sha']:r for r in doc['commits']};trees={}
    for i,c in enumerate(chain):
        r=by_sha[c]
        need(field(r,'commit','verification','verified') is True and field(r,'commit','verification','reason')=='valid','commit not Verified in the stored record: '+c)
        tree=field(r,'commit','tree','sha');local_tree=git_tree(c)
        need(isinstance(tree,str) and tree==local_tree,'stored tree differs from local git: '+c)
        parents=[field(p,'sha') for p in r.get('parents',[])] if isinstance(r.get('parents'),list) else None
        need(parents is not None and parents==git_parents(c),'stored parents differ from local git: '+c)
        if i:need(parents==[chain[i-1]],'stored parent differs from the chain: '+c)
        trees[c]=tree
    need(git('rev-list','--reverse',base+'..'+head).decode().split()==chain[1:],'local commit order differs from the chain')
    if base==BASE:need(trees[base]==BASE_TREE,'base tree differs')
    return dict(chain=chain,verified=True,trees=trees,head_tree=trees[head],records=spec['path'],records_sha256=spec['sha256'],
        compare_used=False,claim='各 commit の tree のハッシュが手元の git と同じ＝その commit の全ファイルの中身が同じ / equal tree hashes: identical content of every path')

def list_digest(paths):
    """The SHA-256 of a sorted path list: UTF-8, one path per line, joined by "\\n", no trailing newline."""
    return sha('\n'.join(paths).encode('utf-8'))

def verify_changed(listed,aidlc_spec,base,head):
    """(2) local git only: paths outside aidlc/ equal the binding's list; aidlc/ count and list digest equal the binding."""
    need(isinstance(listed,list) and all(isinstance(p,str) for p in listed) and listed==sorted(set(listed)),'changed file list is not a sorted unique list')
    need(not any(in_aidlc(p) for p in listed),'binding changed file list names a path inside aidlc/ (only paths outside aidlc/ are listed)')
    need(isinstance(aidlc_spec,dict) and set(aidlc_spec)=={'count','sha256'} and isinstance(aidlc_spec['count'],int) and not isinstance(aidlc_spec['count'],bool)
        and isinstance(aidlc_spec['sha256'],str) and HEX64.fullmatch(aidlc_spec['sha256']) is not None,'binding aidlc_changed differs from {count, sha256}')
    local=sorted(p.decode('utf-8') for p in git('diff-tree','-r','-z','--no-renames','--name-only',base,head).split(b'\0') if p)
    product=[p for p in local if not in_aidlc(p)];inside=[p for p in local if in_aidlc(p)]
    need(product==listed,'changed product files differ between the binding and local git: binding '+str(len(listed))+', local '+str(len(product)))
    need(len(inside)==aidlc_spec['count'],'changed aidlc/ file count differs between the binding and local git: binding '+str(aidlc_spec['count'])+', local '+str(len(inside)))
    digest=list_digest(inside)
    need(digest==aidlc_spec['sha256'],'changed aidlc/ file list SHA-256 differs between the binding and local git')
    return dict(product=listed,aidlc=dict(count=len(inside),sha256=digest,source='手元の git だけ / local git only',
        digest_rule='UTF-8、1 行に 1 つ、"\\n" でつなぎ最後に改行なし / UTF-8, one path per line joined by "\\n", no trailing newline'),
        compare=dict(used=False,note='GitHub の compare は使わない（ファイルの一覧も status も見ない）。系譜は各 commit の記録と手元の git で確かめる / the GitHub compare is not used'))

# ---- (4) CI, (5) performance, (6) upstream ----------------------------------
def base_job_sets():
    d=strict_json(read(BASE_JOBS),'base CI jobs');need(d['head']==BASE and d['repository']==REPOSITORY,'base CI jobs head differs');sets={}
    for r in d['runs']:
        s=sorted(j[0] for j in r['jobs']);need(sets.setdefault(r['name'],s)==s,'base job sets differ within a workflow: '+r['name'])
    need(set(sets)==set(REQUIRED_WORKFLOWS),'base CI jobs do not cover the required workflows')
    return sets

def verify_rerun(r,allow,expected):
    """An allowed attempt 2, checked against the stored attempt-1 job list: exactly the named job (name and id) failed
    in attempt 1 and every other attempt-1 job succeeded; attempt 2 re-ran only that job; every attempt-2 job succeeded."""
    a=r.get('attempt_1');need(isinstance(a,dict) and r['run_attempt']==2,'rerun record missing: '+str(r['id']))
    need(isinstance(allow,dict) and set(allow)=={'job_name','job_id','approval'},'rerun allowance key set differs: '+str(r['id']))
    need(isinstance(allow.get('approval'),str) and allow['approval'].strip(),'rerun has no approval statement: '+str(r['id']))
    failed=[j for j in a['jobs'] if j[2]!='success']
    need(len(failed)==1 and failed[0][0]==allow['job_name'] and failed[0][1]==allow['job_id'] and failed[0][2]=='failure','attempt-1 failed job differs from the allowance: '+str(r['id']))
    need(len(a['failures'])==1 and a['failures'][0]['job_id']==allow['job_id'] and a['failures'][0]['name']==allow['job_name'],'attempt-1 failure record differs: '+str(r['id']))
    need(a['total_count']==len(a['jobs']) and sorted(j[0] for j in a['jobs'])==expected,'attempt-1 job set differs: '+str(r['id']))
    again=[j for j in r['jobs'] if j[3]>=r['run_started_at']]
    need(len(again)==1 and again[0][0]==allow['job_name'],'attempt 2 re-ran other jobs: '+str(r['id']))
    return dict(run_id=r['id'],attempt_1_failed_job=dict(name=failed[0][0],id=failed[0][1]),attempt_1_other_jobs_success=len(a['jobs'])-1,
        attempt_2_rerun_job=dict(name=again[0][0],id=again[0][1]),checked_against='保存した attempt 1 の job の一覧（その job だけが失敗） / the stored attempt-1 job list (only that job failed)',approval=allow['approval'])

def verify_ci(spec,jobs_spec,head,repo):
    need(isinstance(spec,dict) and set(spec)=={'path','sha256','branch','workflows','runs','reruns','job_sets'},'CI binding key set differs')
    need(isinstance(jobs_spec,dict) and set(jobs_spec)=={'path','sha256'},'CI jobs binding key set differs')
    pinned(spec['path'],spec['sha256'],'CI record');pinned(jobs_spec['path'],jobs_spec['sha256'],'CI jobs record')
    doc=strict_json(read(spec['path']),'CI record');jobs=strict_json(read(jobs_spec['path']),'CI jobs record')
    need(doc['repository']==repo==jobs['repository'] and jobs['head']==head,'CI record repository/head differs')
    need(doc['branch']=={'name':spec['branch'],'head':head},'CI record branch head differs')
    wf=spec['workflows'];runs=spec['runs'];reruns=spec['reruns']
    need(isinstance(wf,list) and wf and len(set(wf))==len(wf),'CI workflow set differs')
    need(set(REQUIRED_WORKFLOWS)<=set(wf),'CI workflow set drops a required workflow: '+', '.join(sorted(set(REQUIRED_WORKFLOWS)-set(wf))))
    need(sorted(e['name'] for e in runs.values())==sorted(wf),'CI runs do not cover exactly the workflow set')
    need(isinstance(reruns,dict) and len(reruns)<=MAX_RERUNS,'rerun allowances exceed the limit of '+str(MAX_RERUNS)+' per binding')
    need(set(reruns)<=set(runs),'rerun names a run outside the set')
    for rid,e in runs.items():need(e=={'name':e['name'],'run_attempt':2 if rid in reruns else 1},'CI run attempt differs from the allowance: '+rid)
    stored={str(r['id']):r for r in doc['runs']}
    need(set(stored)==set(runs) and len(doc['runs'])==len(runs),'stored CI runs differ from the binding')
    listed=doc['runs_listed_for_head'];need(listed['total_count']==len(listed['ids'])==len(runs) and {str(i) for i in listed['ids']}==set(runs),'CI run listing for the head differs')
    for rid,r in stored.items():
        need(r['name']==runs[rid]['name'] and r['run_attempt']==runs[rid]['run_attempt'],'stored CI run differs: '+rid)
        need(r['status']=='completed' and r['conclusion']=='success','CI run not completed/success: '+rid)
        need(r['head_sha']==head and r['repository']==repo and r['head_repository']==repo,'CI run head/repository differs: '+rid)
    base_sets=base_job_sets();overrides=spec['job_sets']
    for name,o in overrides.items():
        need(name in wf and set(o)=={'jobs','approval'} and isinstance(o['approval'],str) and o['approval'].strip() and isinstance(o['jobs'],list),'job set override lacks an approval: '+name)
        need(o['jobs'] and all(isinstance(j,str) for j in o['jobs']),'job set override is empty: '+name)
        need(set(base_sets.get(name,[]))<=set(o['jobs']),'job set override drops base jobs: '+name)
    by_id={str(r['id']):r for r in jobs['runs']};need(set(by_id)==set(runs) and len(jobs['runs'])==len(runs),'stored CI job runs differ from the binding')
    out_runs={};out_reruns=[]
    for rid,r in sorted(by_id.items()):
        name=runs[rid]['name'];expected=sorted(overrides[name]['jobs']) if name in overrides else base_sets.get(name)
        need(expected is not None,'workflow has no base job set and no approved new set: '+name)
        need(r['name']==name and r['run_attempt']==runs[rid]['run_attempt'] and r['conclusion']=='success','CI job run differs: '+rid)
        need(r['total_count']==len(r['jobs']) and r['jobs'] and all(j[2]=='success' for j in r['jobs']),'CI job failed or job count differs: '+rid)
        need(sorted(j[0] for j in r['jobs'])==expected,'CI job set differs from the expected set: '+name)
        if rid in reruns:out_reruns.append(verify_rerun(r,reruns[rid],expected))
        else:need('attempt_1' not in r,'attempt-1 record on a run that is not an allowed rerun: '+rid)
        out_runs[rid]=dict(name=name,run_attempt=r['run_attempt'],jobs=len(r['jobs']),job_set='approved new set' if name in overrides else 'equal to the base (e3c29d1d) set')
    diff=dict(added_workflows=sorted(set(wf)-set(REQUIRED_WORKFLOWS)),job_set_overrides={n:dict(added_jobs=sorted(set(o['jobs'])-set(base_sets.get(n,[]))),approval=o['approval']) for n,o in sorted(overrides.items())},
        reruns={rid:dict(job_name=a['job_name'],job_id=a['job_id'],approval=a['approval']) for rid,a in sorted(reruns.items())},rerun_limit=MAX_RERUNS)
    return dict(record=spec['path'],record_sha256=spec['sha256'],jobs_record=jobs_spec['path'],jobs_record_sha256=jobs_spec['sha256'],runs=out_runs,reruns=out_reruns,differences_from_base=diff),runs

def verify_performance(perf,arts_spec,runs,head):
    """(5) for every run of the fixed performance workflow: the u11-node artifact of that run in the stored API artifact list
    (not expired, of the fork's repository id), the ZIP's SHA-256 and size equal that record's digest and size, and the ZIP
    member is the original with passed: true for head."""
    need(isinstance(perf,dict) and set(perf)=={'workflows','runs'},'performance binding key set differs')
    need(perf['workflows']==[PERF_WORKFLOW],'performance workflow is not '+PERF_WORKFLOW)
    need(isinstance(arts_spec,dict) and set(arts_spec)=={'path','sha256'},'CI artifacts binding key set differs')
    pinned(arts_spec['path'],arts_spec['sha256'],'CI artifacts record');arts=strict_json(read(arts_spec['path']),'CI artifacts record')
    need(arts['repository']==REPOSITORY and arts['head']==head,'CI artifacts record repository/head differs')
    by_run={str(r['id']):r for r in arts['runs']}
    expected={rid for rid,e in runs.items() if e['name']==PERF_WORKFLOW}
    need(expected and set(perf['runs'])==expected,'performance runs differ from the runs of the performance workflow')
    out={}
    for rid,e in sorted(perf['runs'].items()):
        need(set(e)=={'path','sha256','artifact'} and isinstance(e['artifact'],dict) and set(e['artifact'])=={'id','zip_path'},'performance entry differs: '+rid)
        rec=by_run.get(rid);need(isinstance(rec,dict) and rec.get('name')==PERF_WORKFLOW and rec.get('total_count')==len(rec.get('artifacts',[])),'stored artifact list missing for the run: '+rid)
        node=[a for a in rec['artifacts'] if a['name']=='u11-node'];need(len(node)==1,'stored artifact list has not exactly one u11-node: '+rid)
        a=node[0];need(a['id']==e['artifact']['id'],'u11-node artifact id differs from the stored record: '+rid)
        need(a['workflow_run']['id']==int(rid) and a['workflow_run']['head_sha']==head,'u11-node artifact does not belong to the run at the head: '+rid)
        need(a['workflow_run'].get('repository_id')==REPOSITORY_ID,'u11-node artifact repository_id is not the fork ('+str(REPOSITORY_ID)+'): '+rid)
        need(a.get('expired') is False,'u11-node artifact is expired or its expired flag is missing: '+rid)
        raw=read(e['artifact']['zip_path']);need('sha256:'+sha(raw)==a['digest'] and len(raw)==a['size_in_bytes'],'u11-node ZIP differs from the stored API digest: '+rid)
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z:member=z.read('performance/observations.json')
        except (zipfile.BadZipFile,KeyError) as error:raise Refusal('u11-node ZIP member missing: '+rid) from error
        original=read(e['path']);need(sha(original)==e['sha256'] and member==original,'performance original differs from the ZIP member: '+rid)
        o=strict_json(original,'performance original')
        need(o.get('head')==head,'performance original head differs: '+rid)
        need(o.get('passed') is True and o.get('complete') is True and isinstance(o.get('result'),dict) and o['result'].get('pass') is True,'performance passed is not true: '+rid)
        out[rid]=dict(original=e['path'],sha256=e['sha256'],artifact_id=a['id'],digest=a['digest'],digest_source=arts_spec['path'],repository_id=REPOSITORY_ID,expired=False,
            p=o['result'].get('p'),mean_interpreter=o['result'].get('meanInterpreter'),mean_jit=o['result'].get('meanJit'),passed=True)
    return out

def verify_upstream(u,head):
    if u is None:return dict(used=False,note='このbindingではupstreamのheadを使わない / not used by this binding')
    need(isinstance(u,dict) and set(u)=={'repository','head','tree_equal','ci','ci_jobs'} and u['repository']==UPSTREAM_REPOSITORY and u['tree_equal'] is True,'upstream binding differs')
    need(isinstance(u['head'],str) and HEX40.fullmatch(u['head']) is not None,'upstream head is not a commit id')
    tree=git_tree(head);doc=strict_json(read(u['ci']['path']),'upstream CI record')
    r={c.get('sha'):c for c in doc['commits']}.get(u['head'])
    need(isinstance(r,dict) and r.get('verified') is True and r.get('reason')=='valid','upstream head not Verified in the stored record')
    need(r.get('tree')==tree,'upstream head tree differs from the head tree')
    local=git_has_commit(u['head'])
    if local:need(git_tree(u['head'])==tree,'local upstream head tree differs from the head tree')
    ci,_=verify_ci(u['ci'],u['ci_jobs'],u['head'],UPSTREAM_REPOSITORY)
    return dict(used=True,head=u['head'],tree=tree,tree_scope='tree 全体（aidlc/ を含む） / the whole tree, aidlc/ included',tree_checked_in_local_git=local,ci=ci)

# ---- whole check -------------------------------------------------------------
def verify(b,trace=None):
    trace=trace if trace is not None else {}
    def stage(s):trace['stage']=s
    stage('binding shape');check_binding_shape(b);head=b['head']
    stage('(0) base records and history');base=verify_base_records();history=verify_history()
    stage('(4) CI');ci,runs=verify_ci(b['ci'],b['ci_jobs'],head,REPOSITORY)
    stage('(1) signature and lineage (commit records)');lineage=verify_lineage(b['commit_records'],b['commit_chain'],BASE,head)
    stage('(2) changed files (local git)');changed=verify_changed(b['changed_files'],b['aidlc_changed'],BASE,head)
    stage('(5) performance');perf=verify_performance(b['performance'],b['ci_artifacts'],runs,head)
    stage('(6) upstream');upstream=verify_upstream(b['upstream'],head)
    stage('(3) working copy');wc=verify_working_copy(head,b['exclusions'])
    return dict(head=head,base=BASE,base_records=base,history=history,lineage=lineage,changed_paths=changed['product'],aidlc_changed_paths=changed['aidlc'],
        compare=changed['compare'],ci=ci,performance=perf,upstream=upstream,working_copy=wc)

CLAIMED_JA=['起点e3c29d1dの記録（入口v4がexit 0になったcheckpointの検証435bc5e0…の記録の写し、その出力result.json、e3c29d1dのCIの記録・artifactの一覧、FR8.3の原本とZIP）と、v1〜v4の入口・binding-08〜11・回帰、この入口の前の版（entry.py・entry-b.py・entry-c.py・entry-d.py・binding-e01〜e04・回帰）のbytesが固定のとおりであること（これらは実行していない）',
    '保存した各commitの記録（GitHubのcommitのAPIの写し）が起点からheadまでの並びのcommitをちょうど含み、どのcommitもVerifiedで、treeのハッシュが手元のgitのtreeと同じで、親が手元のgitの親と並びのとおりであること。treeのハッシュが同じなので、GitHubと手元のgitでそのcommitの全ファイルの中身が同じ。GitHubのcompareは使っていない',
    '起点とheadの差のファイルを手元のgitだけで数え、aidlc/の外の一覧がbindingとちょうど同じで、aidlc/の中の件数と並べた一覧のSHA-256がbindingと同じであること',
    'headのtreeのaidlc/の外の全ファイル（.gitignoreと、名前の除外に当たる場所の追跡ファイルを含む）について、今の作業コピーのbytesがheadのblobと同じであること（bytesの違いを許したのは.aidlc-versionとmise.tomlの2つだけ）。headのtreeに無いパスは、承認済みの名前の除外に当たるか、headのtreeにある.gitignoreの規則でgitが無視するもの（git check-ignore --no-index、読み取りだけ、利用者・システムのgitの設定は読まない）だけであること。名前で除外したものはexcluded_by_name、gitの無視で除外したものはexcluded_by_git_ignoreに列挙',
    '保存したheadのCIの記録が、e3c29d1dの必須の7 workflowを含むbindingのworkflowの集合をちょうど含み、全部completed・successで、attemptは1（bindingで名前とidを挙げた再実行だけattempt 2。再実行の許可はbindingあたり'+str(MAX_RERUNS)+'つまで。保存したattempt 1のjobの一覧でその1 jobだけが失敗）、各runのjobの集合がe3c29d1dの同じworkflowと同じ（または、それを含む人の承認付きの新しい集合）であること',
    'U14 current full qualityの各runのu11-nodeのartifactが、保存したAPIのartifactの一覧でそのrunとheadとforkのrepository_idに属し、expiredがfalseで、ZIPのSHA-256と大きさがその一覧のdigestと大きさに同じで、その中のperformance/observations.jsonがheadについてpassed: trueであること']
CLAIMED_EN=['The base e3c29d1d records (the copy of checkpoint verification 435bc5e0..., where entry v4 exited 0, its result.json, the stored e3c29d1d CI and artifact list, the FR8.3 original and ZIP) and the bytes of the v1-v4 entries, binding-08..11 and their regressions, and of the earlier versions of this entry (entry.py, entry-b.py, entry-c.py, entry-d.py, binding-e01..e04 and their regressions) equal their pins (none of them is executed).',
    "The stored commit records (copies of GitHub's commit API) cover exactly the chain from the base to the head; every commit is Verified, its tree hash equals local git's tree and its parents equal local git's parents and the chain. Equal tree hashes mean GitHub and local git hold the same content for every path of each commit. The GitHub compare is not used.",
    'The files changed between the base and the head are counted from local git only: the list outside aidlc/ equals the binding exactly, and the aidlc/ count and the SHA-256 of the sorted aidlc/ list equal the binding.',
    "Every file of the head's tree outside aidlc/ (.gitignore files and tracked files under by-name excluded paths included) has the head's blob bytes in the working copy; only .aidlc-version and mise.toml may differ. Every path not in the head tree matches the approved by-name exclusions or is ignored by a .gitignore rule from the head tree (git check-ignore --no-index, read-only, without user or system git configuration); listed under excluded_by_name and excluded_by_git_ignore.",
    "The stored CI of the head covers exactly the binding's workflows, which include the 7 required workflows of e3c29d1d, all completed/success at attempt 1 (attempt 2 only for the reruns named by the binding, at most "+str(MAX_RERUNS)+" per binding, where the stored attempt-1 job list shows only that job failed), and each run's job set equals the same workflow at e3c29d1d (or an approved new set that contains it).",
    "For every run of U14 current full quality, the u11-node artifact belongs to that run, head and the fork's repository_id in the stored API artifact list and is not expired, the ZIP's SHA-256 and size equal that list's digest and size, and its performance/observations.json has passed: true for the head."]
NOT_CLAIMED_JA=['変わったファイルの中身が正しいこと（この入口が証明するのはbytesとCIの結果だけ。中身は各Unitのレビュー・試験とheadのCIで確かめる）',
    'treeのハッシュの一致が中身の一致を意味するのは、gitのハッシュ（SHA-1）に衝突がないことを前提にしている。保存したcommitの記録がGitHubの今の状態と同じであること（確認のときにGitHubへ問い合わせていない）。署名は保存した記録のVerifiedを信じ、手元では確かめていない',
    '除外に当たったheadに無いファイル（名前で除外したもの・gitが無視するもの）と.aidlc-version・mise.tomlの手元の差の中身、aidlc/の中のファイルの中身、ファイルのmode（実行ビット）。.gitignoreの規則が適切であること',
    '起点より前の各Unitの細かい照合（U1のmodule receipt、U14のcompiled sourceのclosure、旧chainのvalidator）を今回もう一度実行したこと。e3c29d1dで通った記録をハッシュで引き継いだだけである',
    '再実行・job集合の上書きの承認の文が本当に人のものであること（文の有無だけを確かめる。bindingのSHA-256の採用が人の承認になる）',
    '実公開、FR10.1とU15の受け入れ（GAPのまま）','unitの完了・正式な確認コマンドとしての採用（人の承認が必要）','新しい測定・CI・build・publish']
NOT_CLAIMED_EN=["That the content of changed files is correct (this entry proves bytes and CI results only; content is checked by each Unit's review and tests and by the head's CI).",
    "That equal tree hashes mean equal content assumes no collision of git's hash (SHA-1). That the stored commit records still equal GitHub now (no GitHub query is made at check time); signatures are taken from the stored Verified flag, not checked locally.",
    'The content of excluded paths not in the head tree (by name or ignored by git), of the local differences of .aidlc-version and mise.toml, of files inside aidlc/, and file modes (executable bit); nor that the .gitignore rules are appropriate.',
    "That the detailed per-Unit checks before the base (U1 module receipt, U14 compiled-source closure, old-chain validators) were run again; their e3c29d1d pass is inherited by hash only.",
    "That the approval statements of reruns and job-set overrides really come from the person (only their presence is checked; adopting the binding's SHA-256 is the person's approval).",
    'Real publication, FR10.1 and U15 acceptance (both remain GAP).','Unit completion or adoption as the formal verification command (needs the person).','Any new measurement, CI, build or publish.']

def find_binding(pin):
    found=[p for p in sorted(OWN.glob('binding-e*.json')) if not p.is_symlink() and sha(read(HERE+p.name))==pin]
    need(len(found)==1,'--binding-sha256 matches no binding-e*.json in this folder' if not found else 'several bindings share the SHA-256')
    return found[0].name

def check_pins(entry,pin):
    need(isinstance(entry,str) and HEX64.fullmatch(entry) is not None,'--entry-sha256 must be 64 lowercase hex digits')
    need(isinstance(pin,str) and HEX64.fullmatch(pin) is not None,'--binding-sha256 must be 64 lowercase hex digits')
    need(entry==sha(read(HERE+SELF.name)),'--entry-sha256 differs from the SHA-256 of this entry file')
    return find_binding(pin)

def main(argv):
    try:
        need(len(argv)==5 and argv[1]=='--entry-sha256' and argv[3]=='--binding-sha256',USAGE)
        entry,pin=argv[2],argv[4];name=check_pins(entry,pin)
    except (Refusal,OSError) as error:
        print('REFUSED: '+str(error),file=sys.stderr);return 2
    out=OUT_DIR/('run-'+str(time.time_ns())+'-'+str(os.getpid()));out.mkdir()
    trace=dict(stage='load binding')
    try:
        b=strict_json(read(HERE+name),name);need(sha(read(HERE+name))==pin,'binding bytes changed after selection')
        before=verify(b,trace)
        trace['stage']='re-verify';after=verify(b,dict(trace));need(after==before,'inputs changed during validation')
        trace['stage']='re-check pins';need(check_pins(entry,pin)==name,'pins changed during validation')
        wc=before['working_copy']
        result=dict(entry_e3c29d1d_e='PASS',differences_from_base=dict(before['ci']['differences_from_base'],changed_paths=before['changed_paths'],
                aidlc_changed_paths=before['aidlc_changed_paths'],performance_runs=sorted(before['performance']),upstream=before['upstream']['used']),
            command_line=dict(entry_sha256=entry,binding_sha256=pin),entry=HERE+SELF.name,binding=HERE+name,
            head=before['head'],base=BASE,changed_paths=before['changed_paths'],aidlc_changed_paths=before['aidlc_changed_paths'],compare=before['compare'],
            excluded_by_name=wc['excluded_by_name'],excluded_by_git_ignore=wc['excluded_by_git_ignore'],
            exclusion_decision=DECISION_B,decision=DECISION_E,review_response=REVIEW_E,checks=before,
            claimed=CLAIMED_JA,claimed_en=CLAIMED_EN,not_claimed=NOT_CLAIMED_JA,not_claimed_en=NOT_CLAIMED_EN,
            ci_inputs='stored hash-pinned JSON only; no GitHub query at check time',history_executed=False,
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False)
        with (out/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
        print(json.dumps(dict(output=str(out.relative_to(ROOT)),entry_e3c29d1d_e='PASS',head=before['head'],changed_paths=len(before['changed_paths']),
            aidlc_changed_paths=before['aidlc_changed_paths']['count'],excluded_by_name=len(wc['excluded_by_name']),excluded_by_git_ignore=len(wc['excluded_by_git_ignore']),
            FR10_1='GAP',U15_acceptance='GAP',unit_completed=False)))
        return 0
    except Exception as error:
        details=getattr(error,'details',{})
        with (out/'refusal.json').open('x',encoding='utf-8') as f:
            json.dump(dict(entry_e3c29d1d_e='REFUSED',error=str(error),refused_at=trace,details=details,traceback=traceback.format_exc(),
                exclusions_widened=False,note='除外の一覧は人の判断（2026-10-18）のとおりで、それ以上は広げていない / the exclusion list is the person\'s 2026-10-18 decision, not widened further',
                FR10_1='GAP',U15_acceptance='GAP',unit_completed=False,formal_command_adopted=False,new_measurement=False,new_ci=False),f,indent=2,ensure_ascii=False)
        print('REFUSED: '+str(error),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main(sys.argv))
