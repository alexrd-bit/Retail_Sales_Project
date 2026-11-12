"""Run the notebook with THIS interpreter, from a fresh kernel, and save all outputs.
Usage from repository root: python src/run_model_notebook.py
"""
from pathlib import Path
import json
import os
import sys
import tempfile
import time
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
notebook=ROOT/'project/project-model.ipynb'
nb=nbformat.read(notebook,as_version=4)
with tempfile.TemporaryDirectory(prefix='retail-kernel-') as temporary:
    spec=Path(temporary)/'kernels'/'retail-local'
    spec.mkdir(parents=True)
    (spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
         'display_name':'Retail project interpreter','language':'python'}))
    os.environ['JUPYTER_PATH']=temporary+os.pathsep+os.environ.get('JUPYTER_PATH','')
    client=NotebookClient(nb,timeout=500,kernel_name='retail-local',resources={'metadata':{'path':str(ROOT/'project')}})
    start=time.perf_counter()
    client.execute()
    nb.metadata.kernelspec={'name':'python3','display_name':'Python 3','language':'python'}
    nbformat.write(nb,notebook)
    elapsed=time.perf_counter()-start
    print(f'Fresh-kernel execution completed in {elapsed:.1f} seconds; outputs saved.')
    if elapsed>=600:raise RuntimeError('Notebook exceeded the 10-minute limit')
