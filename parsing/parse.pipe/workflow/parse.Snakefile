import os

configfile: 'config.yaml'
os.makedirs(config['output_dir'], exist_ok=True)

hhsearch_dir = os.path.join(config['input_dir'], 'hhsearch')
hhsearch_files = [os.path.join(hhsearch_dir, f) for f in os.listdir(hhsearch_dir) if f.endswith('.hhr') and os.path.isfile(os.path.join(hhsearch_dir, f))]

rule all:
    input:
        os.path.join(config['output_dir'], 'annotations.csv')

rule parse_annotations:
    input:
        hhr_files = hhsearch_files
    output:
        csv = os.path.join(config['output_dir'], 'annotations.csv')
    params:
        script = os.path.join(config['scripts'], 'parse.py')
    conda:
        os.path.join(config['envs'], 'parse.yml')
    shell:
        """
        python {params.script} \
            --hhr-files {input.hhr_files} \
            --output {output.csv}
        """
