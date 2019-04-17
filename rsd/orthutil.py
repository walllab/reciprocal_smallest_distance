'''
Module for handling various textual ortholog serialization formats produced by
RSD or Roundup.

The oldest format is one ortholog per line:
    SubjectId QueryId Distance
Where SubjectId is the id of a sequence from the subject genome which is
orthologous to QueryId, the id of a sequence from the query genome, and
Distance is the maximum likelihood distance estimate from PAML/codeml.
The problem with the oldest format is it confusing to put the subject id first
when by convention the query genome comes first when running the algorithm or
naming files.

The next format is one ortholog per line:
    QueryId SubjectId Distance
There are two problems with this format and the previous one:
    One can not serialize orthologs for multiple pairs of genomes or parameter
    combinations to a single file and some filesystems perform badly when
    handling millions of files.
    When putting multiple sets of orthologs into a single file, one can not
    represent the (admittedly rare) case of having no orthologs for a given
    pair of genomes (and divergence and evalue).

The current format is loosely based on the dat file format used by UniProt.
A set of orthologs starts with a params row, then has 0 or more ortholog rows,
then has an end row.  It is easy to write a streaming parser and can represent
a set of parameters with no orthologs.
Example snippet:
PA      377629  553174  0.2     1e-20
OR      C5BPU7  D9RR02  1.4127
OR      C5BKE0  D9RR03  2.1041
//
PA      502025  521010  0.2     1e-20
//
'''

import io


def orthologsFromStreamGen(handle, version=-1):
    '''
    handle: a stream from which lines containing orthologs are read.
    version: 1 = the old way RSD serialized orthologs: each line has a subject sequence id, query sequence id, paml distance.
    2 = the new, more sensible way RSD serializes orthologs: each line is a tab-separated query sequence id, subject sequence id, paml distance.
    -1 = the default = the latest version, 2.
    returns: a generator that yields orthologs, which are tuples of (query_sequence_id, subject_sequence_id, distance)
    '''
    for line in handle:
        id1, id2, dist = line.split('\t')
        if version == 1: # line is sdb, qdb, dist
            yield id2, id1, dist
        else: # line is qdb, sdb, dist
            yield id1, id2, dist


def orthologsToStream(orthologs, handle, version=-1):
    '''
    orthologs: an iterable of tuples of (query_id, subject_id, distance)
    handle: a stream from which lines containing orthologs are read.
    version: 1 = the old way RSD serialized orthologs: each line has a subject sequence id, query sequence id, paml distance.
    2 = the new, more sensible way RSD serializes orthologs: each line is a tab-separated query sequence id, subject sequence id, paml distance.
    -1 = the default = the latest version, 2.
    returns: a generator that yields orthologs, which are tuples of (query_sequence_id, subject_sequence_id, distance)
    '''
    for ortholog in orthologs:
        qid, sid, dist = ortholog
        if version == 1:
            handle.write('{}\t{}\t{}\n'.format(sid, qid, dist))
        else:
            handle.write('{}\t{}\t{}\n'.format(qid, sid, dist))


#########################################
# ORTHDATAS SERIALIZATION AND PERSISTANCE
#########################################

# orthData: a tuple of params, orthologs.  i.e. ((qdb, sdb, div, evalue), ((qid1, sid1, dist1), (qid2, sid2, dist2), ...))
# params: a tuple of query genome, subject genome, divergence, and evalue.
# orthologs: a list of query id, subject id, and distance.


def orthDatasFromFile(path):
    return list(orthDatasFromFileGen(path))


def orthDatasFromFileGen(path):
    '''
    path: contains zero or more orthDatas.  must exist.
    yields: every orthData, a pair of params and orthologs, in path.
    '''
    with open(path) as fh:
        for orthData in orthDatasFromStreamGen(fh):
            yield orthData


def orthDatasFromFilesGen(paths):
    '''
    paths: a list of file paths containing orthDatas.
    yields: every orthData in every file in paths
    '''
    for path in paths:
        for orthData in orthDatasFromFile(path):
            yield orthData


def orthDatasToFile(orthDatas, path, mode='w'):
    '''
    orthDatas: a list of rsd orthDatas. orthData is a pair of params and orthologs
    path: where to save the orthDatas
    mode: change to 'a' to append to an existing file
    serializes orthDatas and persists them to path
    Inspired by the Uniprot dat files, a set of orthologs starts with a params row, then has 0 or more ortholog rows, then has an end row.
    Easy to parse.  Can represent a set of parameters with no orthologs.
    Example:
    PA\tLACJO\tYEAS7\t0.2\t1e-15
    OR\tQ74IU0\tA6ZM40\t1.7016
    OR\tQ74K17\tA6ZKK5\t0.8215
    //
    PA      MYCGE   MYCHP   0.2     1e-15
    //
    '''
    with open(path, mode) as fh:
        orthDatasToStream(orthDatas, fh)


def orthDatasToStr(orthDatas):
    '''
    orthDatas: a list of rsd orthDatas. orthData is a pair of params and orthologs
    serialize orthDatas as a string.
    returns: a string containing the serialized orthDatas.
    '''
    with io.BytesIO() as handle:
        orthDatasToStream(orthDatas, handle)
        return handle.getvalue()
    

def orthDatasToStream(orthDatas, handle):
    '''
    orthDatas: a list of rsd orthDatas. orthData is a pair of params and orthologs
    handle: an open io stream (e.g. a filehandle or a StringIO) to which the orthDatas are written
    the handle is not opened or closed in this function.
    '''
    for (qdb, sdb, div, evalue), orthologs in orthDatas:
        handle.write('PA\t{}\t{}\t{}\t{}\n'.format(qdb, sdb, div, evalue))
        for ortholog in orthologs:
            handle.write('OR\t{}\t{}\t{}\n'.format(*ortholog))
        handle.write('//\n')
    return handle


def orthDatasFromStreamGen(handle):
    '''
    handle: an open io stream (e.g. a filehandle or a StringIO) from which orthDatas are read and yielded
    yields: every orthData, a pair of params and orthologs, in path.
    '''
    for line in handle:
        if line.startswith('PA'):
            lineType, qdb, sdb, div, evalue = line.strip().split('\t')
            orthologs = []
        elif line.startswith('OR'):
            lineType, qid, sid, dist = line.strip().split('\t')                        
            orthologs.append((qid, sid, dist))
        elif line.startswith('//'):
            yield ((qdb, sdb, div, evalue), orthologs)
    
    
                    
