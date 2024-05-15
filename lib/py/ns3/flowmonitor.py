import re
import xml.etree.ElementTree as ET
import pandas as pd


def xmltime2floatsec(strtime):
    ''' Converting a string format time in xml to a floating number in seconds
    In the flow monitor, the time format is like '+23232.232ns'.
    This function converts the string time with above format to
    a floating number in unit of seconds

    Args:
        strtime: A string representing time
    Returns:
        A floating number representing the time in seconds
    '''
    assert strtime[-2:] == 'ns'
    return float(strtime[:-2])/1e9


def get_fct_breakdown(flow_stats):
    ''' Get Statistics of FCT across different flow sizes

    Args:
        flow_stats: A DataFrame containing flow statistics data
            This is usually from XmlParser.stats_df

    Returns:
        A dictionary contains FCT breakdown
    '''
    df = flow_stats
    small_df = df[df.rxBytes <= (100 << 10)]
    median_df = df[
        (df.rxBytes > (100 << 10)) & (df.rxBytes <= (10 << 20))
    ]
    large_df = df[df.rxBytes > (10 << 20)]
    fct_breakdown = {
        'overall_avg': df['fct'].mean(),
        'small_avg': small_df['fct'].mean(),
        'small_tail': small_df['fct'].quantile(
            0.99, interpolation='lower',
        ),
        'median_avg': median_df['fct'].mean(),
        'large_avg': large_df['fct'].mean(),
    }
    return fct_breakdown


def get_fct_flowsize(flow_stats):
    ''' FCT statistics of different flow sizes
    Args:
        flow_stats: A DataFrame containing flow statistics data
            This is usually from XmlParser.stats_df

    Returns:
        A DataFrame contains FCT statistics vs. flow_size
    '''
    flow_stats = flow_stats.sort_values(by=['rxBytes'])
    df_grouped = flow_stats.groupby('rxBytes')
    stats = []
    for rxBytes, df in df_grouped:
        stats.append({
            'flow_size': rxBytes,
            'avg': df['fct'].mean(),
            'median': df['fct'].quantile(0.5, interpolation='lower'),
            '99th': df['fct'].quantile(0.99, interpolation='lower'),
        })
    fct_flowsize_df = pd.DataFrame(stats)
    return fct_flowsize_df


class XmlParser(object):
    ''' Parse xml file containing flow monitor results

    Attributes:
        fname: The name of xml file
        stats_df: A DataFrame containing flow statistics data
        all_stats_df: A DataFrame containing all flow statistics data,
                      including reversed flow.
        fid2tuples: A dictionary mapping flow id to five tuple
        small_df: A DataFrame containing small flow statistics
        median_df: A DataFrame containing median flow statistics
        large_df: A DataFrame containing large flow statistics
        fct_breakdown: A Dictionary containing breakdown dct statistics
        fct_flowsize_df: A DataFrame containing fct vs. flowsize
    TODO:
        Mapping flow id to five tuple
    '''
    def __init__(self, fname):
        self.fname = fname
        self.parse()

    def parse(self):
        ''' Parsing a xml format file
        Getting flow stat data from the xml file.
        The result is stored in a DataFrame named "self.stats_df",
        in which the index is flow id and columns are flow stats.
        '''
        self.get_classifier()
        flow_stats = {}
        tree = ET.parse(self.fname)
        root = tree.getroot()
        for child in root.findall('FlowStats/Flow'):
            fid = int(child.get('flowId'))
            stats = {}
            for name, value in child.items():
                if value[-2:] == 'ns':
                    stats[name] = xmltime2floatsec(value)
                elif name == 'flowId':
                    continue
                else:
                    stats[name] = int(value)
            flow_stats[fid] = stats
            flow_stats[fid].update(self.fid2tuples[fid])
        df = pd.DataFrame.from_dict(flow_stats, orient='index')
        df['fct'] = df['timeLastRxPacket'] - df['timeFirstTxPacket']
        df['throughput'] = df['rxBytes'] * 8.0 / df['fct']
        self.all_stats_df = df.copy()
        # Delete reverse flows that only containing ACKs
        self.stats_df = df[df.txBytes / df.txPackets > 80].copy()
        return self.stats_df

    def get_fct_breakdown(self):
        ''' Statistics of different flow sizes
        '''
        self.fct_breakdown = get_fct_breakdown(self.stats_df.copy())
        return self.fct_breakdown

    def get_fct_flowsize(self):
        ''' FCT statistics of different flow sizes
        '''
        self.fct_flowsize_df = get_fct_flowsize(self.stats_df.copy())
        return self.fct_flowsize_df

    def get_classifier(self):
        ''' Get the flow classifier from xml file
        The flow classifier is stored into fid2tuples
        '''
        tree = ET.parse(self.fname)
        root = tree.getroot()
        self.fid2tuples = {}
        for child in root.findall('Ipv4FlowClassifier/Flow'):
            fid = int(child.get('flowId'))
            self.fid2tuples[fid] = {
                'srcaddr': child.get('sourceAddress'),
                'dstaddr': child.get('destinationAddress'),
                'protocol': int(child.get('protocol')),
                'srcport': int(child.get('sourcePort')),
                'dstport': int(child.get('destinationPort')),
            }
        return self.fid2tuples
