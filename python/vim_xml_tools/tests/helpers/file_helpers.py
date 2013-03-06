import os.path as p

CURRENT_FOLDER = p.dirname(p.abspath(__file__))
SAMPLES_FOLDER = p.join(CURRENT_FOLDER, "../samples")

def read_sample_xml(path):
    with open(p.join(SAMPLES_FOLDER, path)) as f:
        return f.read()
