import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.dates as mdates


def ridgeline(dataframe, 
              col_time, 
              col_group, 
              col_value,
              dt_format,
              title='', 
              title_loc='center',
              norm='overall', 
              frac=.1, 
              scale=3,
              note=None,
              figsize=(12,8),
              cmap='autumn',
              alpha=.5,
              linspace=(0,1)):
    '''
    Create ridgeline plots for grouped data over time
    
    
        Parameters:
            dataframe (pd.DataFrame): pandas dataframe with time column, group column
                                      and value column
            col_time        (string): time column name
            col_group       (string): group column name
            col_value       (string): value column name
            title           (string): chart title
            title_loc       (string): title position
            norm ('overall'|'group'): type of normalization; divide values column
                                      by overall max or group max
            frac    (0 < float <= 1): fraction of data to use for lowess smoothing
            scale            (float): scale vertically to control overlap
            note             (tuple): (x, y, 'string')
            figsize          (tuple): (width, height)
            cmap            (string): colormap from matplotlib.cm
            alpha            (float): set transparency 
            linspace         (tuple): set range of colormap to use; between 0 and 1
            dt_format       (string): datetime format
        Returns:
            fig, ax          (tuple): matplotlib fig and ax
    '''
    
    # Copy df
    df = dataframe.copy()
    
    # Normalize by overall max value
    if norm == 'overall':
        df['norm'] = df[col_value].div(df[col_value].max())
    elif norm== 'group':
        groupmax = df.groupby(col_group)[col_value].transform('max')
        df['norm'] = df[col_value].div(groupmax)
    else:
        raise ValueError
    
    # Sort on group/time
    df.sort_values(by=[col_group, col_time], inplace=True)
    
    # Create smoothed line
    lowess = sm.nonparametric.lowess
    for group in df[col_group].unique():
        df_sub = df.query(f'{col_group} == "{group}"')
        smoothed = lowess(df_sub.norm, df_sub[col_time], is_sorted=True, return_sorted=False, frac=frac)
        df.loc[df[col_group] == group, 'smoothed_norm'] = smoothed.clip(min=0)
    
    # Create scaled group indicator
    df[col_group] = df[col_group].astype('category')
    df['group_id'] = (df[col_group].cat.codes + 1) / scale
    
    # Create columns for plotting
    df['smoothed_norm_plot'] = df.smoothed_norm + df.group_id
    df['norm_plot'] = df.norm + df.group_id
                         
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get colormap
    clmap = plt.get_cmap(cmap)
    colors = iter(clmap(np.linspace(linspace[0],linspace[1],len(df.province.unique()))))
    
    # Loop over reversed group list, create area chart for each group
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
                     xy=(df_sub[col_time].min(), df_sub.group_id.min()), 
                     textcoords='offset points', 
                     xytext=(-70,0))
    
    # Figure formatting
    ax.axes.get_yaxis().set_visible(False)
    plt.box(on=None)
    ax.set_xlim([df[col_time].min(), df[col_time].max()])
    ax.xaxis.set_major_formatter(mdates.DateFormatter(dt_format))
    plt.title(title, color='black',fontsize=15,fontweight='roman',loc=title_loc)
    if note is not None:
        fig.text(note[0], note[1], note[2])
        
    return fig, ax
