import os

configfile: 'config.yaml'
os.makedirs(config['output_dir'], exist_ok=True)

samples = [os.path.splitext(sample)[0] for sample in os.listdir(config['input_dir'])
           if sample.startswith('GC') and sample.endswith('_repr.faa')]


databases = ['pfam', 'pdb', 'cdd']

rule all:
    input:
        expand(os.path.join(config['output_dir'], 'hhsearch', '{sample}_{db}.hhr'), sample=samples, db=databases)
        
rule select_longest:
    input:
        fasta = os.path.join(config['input_dir'], '{sample}.faa')
    output:
         fasta = os.path.join(config['output_dir'], 'longest_output', '{sample}.faa')
    params:
         longest_dir = lambda wc: os.path.join(config['output_dir'], 'longest_output'),
         scripts = os.path.join(config['scripts'], 'select.py')
    conda:
         os.path.join(config['envs'], 'select.yml')
    shell:
        """
        mkdir -p {params.longest_dir}
        python {params.scripts} --input {input.fasta} --output {output.fasta}
        """

rule hhsearch:
    input:
        fasta = os.path.join(config['output_dir'], 'longest_output', '{sample}.faa')
    output:
        hhr = os.path.join(config['output_dir'], 'hhsearch', '{sample}_{db}.hhr')
    params:
        db_path = lambda wc: config['databases'][wc.db],
        evalue = config['evalue'],
        threads = config['threads'],
        hhsearch_dir = lambda wc: os.path.join(config['output_dir'], 'hhsearch')
    conda:
        os.path.join(config['envs'], 'hhsearch.yml')
    shell:
        """
        mkdir -p {params.hhsearch_dir}
        hhsearch -i {input.fasta} -d {params.db_path} -o {output.hhr} -e {params.evalue} -cpu {params.threads}
        """
