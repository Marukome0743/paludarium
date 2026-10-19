"""Save the GitHub records of head 27d05de1 for entry-f.py (U15 Step 28).

Read-only `gh api` GETs only (no rerun, dispatch or write). Writes, in this folder:
  ci-27d05de1.json, ci-jobs-27d05de1.json, ci-artifacts-27d05de1.json,
  u14-quality-<run>/artifact-zip/u11-node-<id>.zip and u14-quality-<run>/u11-node/performance/observations.json,
  u12-quality-<run>/attempt-1/job-<id>.log
and ../entry-e3c29d1d/commits-27d05de1.json. Refuses to overwrite an existing file.
"""
import io,json,subprocess,sys,zipfile
from pathlib import Path

REPO='Marukome0743/paludarium'
BASE='e3c29d1d8c2dae3c705d54de2c6fb0a2451e46d9'
HEAD='27d05de165c703f4681fcf1789b1bf6defd97f47'
CHAIN=[BASE,'8b415a7cffa8ed2b03e70e31f5339ea1dfd05e1e','8360be2eb10c5c3848582aaba303dc89a35b56a3',HEAD]
BRANCH='codex/build-and-test'
RERUN={'run':39149189719,'job':117739162319}
PERF_RUN=39149187727
DATE='2026-10-19 JST'
HERE=Path(__file__).resolve().parent
ENTRY_DIR=HERE.parent/'entry-e3c29d1d'

def gh(path,raw=False):
    out=subprocess.run(['gh','api','-H','Accept: application/vnd.github+json',*(['--allow-escape-sequences'] if raw else []),path],capture_output=True,check=True).stdout
    return out if raw else json.loads(out)

def pages(path,key):
    items=[];page=1
    while True:
        d=gh(f'{path}{"&" if "?" in path else "?"}per_page=100&page={page}');items+=d[key]
        if len(items)>=d['total_count'] or not d[key]:return items,d['total_count']
        page+=1

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(data if isinstance(data,bytes) else (json.dumps(data,ensure_ascii=False,indent=1)+'\n').encode())

def job_rows(run,attempt):
    jobs,total=pages(f'repos/{REPO}/actions/runs/{run}/attempts/{attempt}/jobs','jobs')
    for j in jobs:
        assert j['status']=='completed' and j['run_attempt']==attempt and j['head_sha']==HEAD,(run,j['name'])
    return [[j['name'],j['id'],j['conclusion'],j['started_at']] for j in jobs],total

def main():
    commits=[gh(f'repos/{REPO}/commits/{c}') for c in CHAIN]
    write(ENTRY_DIR/'commits-27d05de1.json',dict(schema=1,
        source=f'gh api (read-only GET), {DATE}: fields sha, parents[].sha, commit.tree.sha, commit.verification.verified and commit.verification.reason copied from GET repos/{REPO}/commits/<sha> for every commit of the chain e3c29d1d..27d05de1.',
        repository=REPO,commits=[dict(sha=c['sha'],parents=[dict(sha=p['sha']) for p in c['parents']],
            commit=dict(tree=dict(sha=c['commit']['tree']['sha']),verification=dict(verified=c['commit']['verification']['verified'],reason=c['commit']['verification']['reason']))) for c in commits]))
    listed,total=pages(f'repos/{REPO}/actions/runs?head_sha={HEAD}','workflow_runs')
    ids=sorted(r['id'] for r in listed)
    runs=[gh(f'repos/{REPO}/actions/runs/{i}') for i in ids]
    keys=['id','run_attempt','name','path','event','head_sha','head_branch','status','conclusion','created_at','run_started_at','updated_at']
    branch=gh(f'repos/{REPO}/branches/{BRANCH.replace("/","%2F")}')
    write(HERE/'ci-27d05de1.json',dict(schema=1,
        source=f'gh api (read-only GET), {DATE}; fields copied from GET repos/{REPO}/actions/runs/{{id}} (latest attempt; attempt 1 for every run except U12 current full quality {RERUN["run"]}, whose latest attempt is 2), GET repos/{REPO}/commits/{{sha}}, GET repos/{REPO}/branches/codex%2Fbuild-and-test and GET repos/{REPO}/actions/runs?head_sha={HEAD}. No compare (entry-f does not use it).',
        repository=REPO,branch=dict(name=branch['name'],head=branch['commit']['sha']),
        commits=[dict(sha=c['sha'],parents=[p['sha'] for p in c['parents']],tree=c['commit']['tree']['sha'],verified=c['commit']['verification']['verified'],reason=c['commit']['verification']['reason']) for c in commits],
        runs=[dict({k:r[k] for k in keys},repository=r['repository']['full_name'],head_repository=r['head_repository']['full_name']) for r in runs],
        runs_listed_for_head=dict(total_count=total,ids=ids)))
    job_runs=[]
    for r in runs:
        rows,count=job_rows(r['id'],r['run_attempt'])
        e=dict(id=r['id'],name=r['name'],run_attempt=r['run_attempt'],run_started_at=r['run_started_at'],conclusion=r['conclusion'],total_count=count,jobs=rows)
        if r['id']==RERUN['run']:
            a1=gh(f'repos/{REPO}/actions/runs/{r["id"]}/attempts/1');rows1,count1=job_rows(r['id'],1)
            job=gh(f'repos/{REPO}/actions/jobs/{RERUN["job"]}')
            step=[s for s in job['steps'] if s['conclusion']=='failure']
            assert len(step)==1
            log=gh(f'repos/{REPO}/actions/jobs/{RERUN["job"]}/logs',raw=True)
            logp=HERE/f'u12-quality-{r["id"]}/attempt-1/job-{RERUN["job"]}.log';write(logp,log)
            assert b'Failed to connect to apt.llvm.org port 443' in log
            e['attempt_1']=dict(run_started_at=a1['run_started_at'],conclusion=a1['conclusion'],total_count=count1,
                failures=[dict(job_id=job['id'],name=job['name'],failed_step=f'{step[0]["number"]} {step[0]["name"]}',
                    cause="The step could not reach apt.llvm.org: curl: (7) Failed to connect to apt.llvm.org port 443 after 4001 ms (exit 7), while preparing the LLVM symbolizer, after the fuzz build and before any fuzzing ran; outside the product. The person chose to rerun this failed job only (原文：「U12 current full quality（run 39149189719）の失敗した job「u12-fuzz / fuzz (vfs_paths)」（job 117739162319）だけをやり直してください。原因は apt.llvm.org につながらなかったことです。」).")],
                jobs=rows1)
        job_runs.append(e)
    write(HERE/'ci-jobs-27d05de1.json',dict(schema=1,
        source=f'gh api (read-only GET), {DATE}; rows [name, id, conclusion, started_at] copied from GET repos/{REPO}/actions/runs/{{id}}/attempts/{{n}}/jobs?per_page=100 for the latest attempt n (n = 1 for every run except U12 current full quality {RERUN["run"]}, n = 2); for that run attempt 1 is also recorded (GET .../attempts/1 and .../attempts/1/jobs). Every listed job has status completed, run_attempt equal to its attempt and head_sha {HEAD}; total_count is the API count. The failure cause is from GET .../actions/jobs/{RERUN["job"]} (its steps) and the job log saved at verification/ci-27d05de1/u12-quality-{RERUN["run"]}/attempt-1/job-{RERUN["job"]}.log.',
        repository=REPO,head=HEAD,runs=job_runs))
    arts,count=pages(f'repos/{REPO}/actions/runs/{PERF_RUN}/artifacts','artifacts')
    write(HERE/'ci-artifacts-27d05de1.json',dict(schema=1,
        source=f'gh api (read-only GET), {DATE}; fields id, name, size_in_bytes, digest, expired, workflow_run.id, workflow_run.head_sha, workflow_run.repository_id copied from GET repos/{REPO}/actions/runs/{PERF_RUN}/artifacts?per_page=100 (U14 current full quality at 27d05de1), total_count is the API count.',
        repository=REPO,head=HEAD,runs=[dict(id=PERF_RUN,name='U14 current full quality',total_count=count,artifacts=[dict(id=a['id'],name=a['name'],size_in_bytes=a['size_in_bytes'],digest=a['digest'],expired=a['expired'],
            workflow_run=dict(id=a['workflow_run']['id'],head_sha=a['workflow_run']['head_sha'],repository_id=a['workflow_run']['repository_id'])) for a in arts])]))
    node=[a for a in arts if a['name']=='u11-node'];assert len(node)==1
    raw=gh(f'repos/{REPO}/actions/artifacts/{node[0]["id"]}/zip',raw=True)
    write(HERE/f'u14-quality-{PERF_RUN}/artifact-zip/u11-node-{node[0]["id"]}.zip',raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:member=z.read('performance/observations.json')
    write(HERE/f'u14-quality-{PERF_RUN}/u11-node/performance/observations.json',member)
    print(json.dumps(dict(runs=len(runs),listed=total,artifact=node[0]['id'],zip_bytes=len(raw))))

if __name__=='__main__':sys.exit(main())
