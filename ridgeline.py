import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd


def ridgeline(dataframe, 
              ax,
              col_time, 
              col_group, 
              col_value,
              norm='overall', 
              frac=.1, 
              scale=3,
              colormap='autumn',
              alpha=.5,
              linspace=(0,1),
              sort_groups=None,
              labeloffset=-70):
    '''
    Create ridgeline plots for grouped data over time

        Parameters:
            dataframe (pd.DataFrame): pandas dataframe with time column, group column
                                      and value column
            col_time        (string): time column name, needs to be pd.datetime or numeric
            col_group       (string): group column name, column dtype must be string
            col_value       (string): value column name
            title           (string): chart title
            title_loc       (string): title position
            norm ('overall'|'group'): type of normalization; divide values column
                                      by overall max or group max
            frac    (0 < float <= 1): fraction of data to use for lowess smoothing
            scale            (float): scale vertically to control overlap
            note             (tuple): (x, y, 'string')
            figsize          (tuple): (width, height)
            colormap        (string): colormap from matplotlib.cm
            alpha            (float): set transparency 
            linspace         (tuple): set range of colormap to use; between 0 and 1
            dt_format       (string): datetime format
            sort_groups       (list): sorted list of groups to include
            labeloffset      (float): horizontal label affset
        Returns:
            ax          (tuple): matplotlib ax
    '''
    
    # Copy df
    df = dataframe.copy()            
    
    # Normalize by overall max value
    if norm == 'overall':
        df['norm'] = df[col_value].div(df[col_value].max())
    elif norm == 'group':
        groupmax = df.groupby(col_group)[col_value].transform('max')
        df['norm'] = df[col_value].div(groupmax)
    else:
        raise ValueError
    
    # Sort on group/time
    df.sort_values(by=[col_group, col_time], inplace=True)
    
    # Create smoothed line
    lowess = sm.nonparametric.lowess
    for group in df[col_group].unique():
        df_sub = df[df[col_group] == group]
        smoothed = lowess(df_sub.norm, df_sub[col_time], is_sorted=True, return_sorted=False, frac=frac)
        df.loc[df[col_group] == group, 'smoothed_norm'] = smoothed.clip(min=0)
    
    # Create scaled group indicator
    if sort_groups is not None:
        df[col_group] = pd.Categorical(df[col_group], sort_groups)
    else:
        df[col_group] = df[col_group].astype('category')
    df['group_id'] = (df[col_group].cat.codes + 1) / scale
    
    # Create columns for plotting
    df['smoothed_norm_plot'] = df.smoothed_norm + df.group_id
    df['norm_plot'] = df.norm + df.group_id
    
    # Get colormap
    clmap = plt.get_cmap(colormap)
    colors = iter(clmap(np.linspace(linspace[0],linspace[1],len(df[col_group].unique()))))
    
    # Loop over reversed group list, create area chart for each group
    if sort_groups is not None:
        group_list = sort_groups
    else:
        group_list = df[col_group].unique().tolist()
    group_list = group_list[::-1]
    for group in group_list:
        df_sub = df[df[col_group] == group]
        
        # Area chart for each group
        ax.fill_between(col_time, 
                        'smoothed_norm_plot', 
                        'group_id', 
                        data=df_sub, 
                        alpha=alpha, 
                        facecolor=next(colors),
                        edgecolor='white')
        # Group labels
        plt.annotate(group, 
                     xy=(df[col_time].min(), df_sub.group_id.min()), 
                     textcoords='offset points', 
                     xytext=(labeloffset,0))
    
    # Formatting
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xlim([df[col_time].min(), df[col_time].max()])
    ax.axes.get_yaxis().set_visible(False)
        
    del df
        
    return ax
