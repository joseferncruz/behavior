# -*- coding: utf-8 -*-
"""
Behavior - 2020 - LeDoux Lab

Licensed under GNU Lesser General Public License v3.0

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""


##############################################################################

def plot_events(
    ax,
    dataframe,
    cs_id_list,
    rat,
    event_type,
):
    """Plot events pre, peri and post-cs."""
    for index, cs in enumerate(cs_id_list, start=1):
        # Extract one epoch
        epoch = dataframe[f'{event_type}_events'][(dataframe['cs_id'] == cs)
                                                  ].reset_index(drop=True)
        # plot it
        ax.plot(epoch[900:3600]*index,  '|', label=cs)

    # Plot cs
    ax.fill_between([1800, 2700], [10, 10], alpha=0.2)

    # axis properties
    ax.set_xticklabels(['-30', '0', '30', '60'])
    ax.set_xticks([900, 1800, 2700, 3600])
    ax.set_xlabel('time (sec)')
    ax.set_ylabel('cs_id')
    ax.set_ylim(0.1, index+0.8)
    ax.set_yticklabels([])

    # Add an arrow to label the cs start
    ax.annotate('',
                xy=(1800, index+0.2),
                xytext=(1801, index+0.6),
                arrowprops=dict(facecolor='black', shrink=0.05),
                )
    # title
    ax.set_title(
        f'rat_{rat.animal_id}_{rat.experiment_id}_{rat.session}_{rat.sex}',
        )

    # Reverse legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles),
              reversed(labels),
              loc=(1, 0.2),
              title='cs_id',
              frameon=False,
              )
###############################################################################
