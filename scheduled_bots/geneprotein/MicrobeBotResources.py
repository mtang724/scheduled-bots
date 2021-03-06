"""
Modified from https://bitbucket.org/sulab/wikidatabots/src/226614eeda5f258fc913b10fdcaa3c22c7f64045/genes/microbes/MicrobeBotResources.py?at=jenkins-automation&fileviewer=file-view-default
originally written by timputman

"""
import os
import urllib.request

import pandas as pd
from wikidataintegrator.wdi_helpers import id_mapper

def get_ref_microbe_taxids(force_download=False):
    df = get_microbe_taxids(force_download=force_download)
    df = df[df['refseq_category'].isin(['reference genome'])]
    return df


def get_microbe_taxids(force_download=False):
    """
    Download the latest bacterial genome assembly summary from the NCBI genome ftp site
    and generate a pd.DataFrame of relevant data for strain items based on taxids of the bacterial reference genomes.
    :return: pandas dataframe of bacteria reference genome data
    """
    if force_download or not os.path.exists("reference_genomes.csv"):
        assembly = urllib.request.urlretrieve("ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt")
        df = pd.read_csv(assembly[0], sep="\t", dtype=object, skiprows=1, header=0)
        df = df[df['refseq_category'].isin(['reference genome', 'representative genome'])]

        all_tax_wdid = id_mapper('P685')

        df['wdid'] = df['taxid'].apply(lambda x: all_tax_wdid.get(x, None))
        df = df.rename(columns={'# assembly_accession': 'assembly_accession'})
        df.to_csv('reference_genomes.csv', sep="\t")
        df.taxid = df.taxid.astype(int)
        return df
    else:  # use predownloaded and parsed flatfile
        df = pd.read_csv("reference_genomes.csv", sep="\t", dtype=object, index_col=0)
        df.taxid = df.taxid.astype(int)
        return df

def get_all_taxa():
    df = get_ref_microbe_taxids()
    ref_taxids = df['taxid'].tolist()
    return ref_taxids

def get_organism_info(taxid):
    df = get_microbe_taxids()
    ref_taxids = df['taxid'].tolist()
    if taxid not in ref_taxids:
        raise ValueError("taxid {} not found in microbe ref genomes".format(taxid))
    organism_info = dict(df.query("taxid == @taxid").iloc[0])
    organism_info['name'] = organism_info['organism_name']
    organism_info['type'] = "microbial"

    return organism_info
