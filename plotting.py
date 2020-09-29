from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import animation
import numpy as np
# from progress.bar import Bar

def static_momentum_plot(match, p1_momentum, p2_momentum, EoS):
    if len(p1_momentum) != len(p2_momentum):
        raise Exception('inputs have mismatched sizes')

    # Initialise figure and main subplot
    fig, main_ax = plt.subplots()

    # Create x-axis values
    x = list(range(len(p1_momentum)))

    # Find range for y-axis
    max_points = match.Rules['SETS_TO_WIN']*match.Rules['GAMES_IN_SET']*match.Rules['POINTS_IN_GAME']
    score_range = [0, max_points]

    # Create ticks and labels for y-axis
    y_ticks = [i*match.Rules['GAMES_IN_SET']*match.Rules['POINTS_IN_GAME'] for i in range(1,match.Rules['SETS_TO_WIN']+1)]
    y_labels = [str(1) + ' set'] + [str(i) + ' sets' for i in range(2,match.Rules['SETS_TO_WIN']+1)]
    y_labels[-1] = 'Win!'
    main_ax.set_yticks(y_ticks)
    main_ax.set_yticklabels(y_labels)
    plt.grid(which='major', axis='y')

    xlabels = [[0,0]]
    current_score=[0,0]
    for set_ in match.Score:
        current_score[set_.Winner]+= 1
        xlabels.append(list(current_score))

    
    # Create title string using match info
    titlestring = match.PrintPlayers() + '\n' + match.Info['TOURNAMENT'] + ' - ' +match.Info['ROUND'] +'\n' + match.Info['DATE'].isoformat()
    main_ax.set_title(titlestring)

    plt.xlim(0, len(x))
    plt.ylim(score_range[0], score_range[1])
    main_ax.set_xlabel('Match progress')
    main_ax.set_ylabel('\"Victory meter\"')
    main_ax.set_xticks(EoS)
    main_ax.set_xticklabels(xlabels)
    for set_end in EoS:
        main_ax.axvline(set_end, linestyle='--', linewidth = 0.3 ,color = 'lightgray')
    main_ax.plot(x, p1_momentum, color='tab:blue', label=match.Players[0].Last)
    main_ax.plot(x, p2_momentum, color='tab:orange', label=match.Players[1].Last)

    main_ax.legend()


    fig.tight_layout()

    plt.show()
    return 0

def momentum_animation(match, p1_momentum, p2_momentum, EoS, save_video=True):
    # https://towardsdatascience.com/how-to-create-animated-graphs-in-python-bb619cc2dec1
    # https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    
    
    # Check that the data is correctly formatted
    if len(p1_momentum) != len(p2_momentum):
        raise Exception('inputs have mismatched sizes')
    
    # Initialise figure and main subplot
    fig, main_ax = plt.subplots()

    # Create x-axis values
    x = list(range(len(p1_momentum)))

    # Find range for y-axis
    max_points = match.Rules['SETS_TO_WIN']*match.Rules['GAMES_IN_SET']*match.Rules['POINTS_IN_GAME']
    score_range = [0, max_points]

    # Create ticks and labels for y-axis
    y_ticks = [i*match.Rules['GAMES_IN_SET']*match.Rules['POINTS_IN_GAME'] for i in range(1,match.Rules['SETS_TO_WIN']+1)]
    y_labels = [str(1) + ' set'] + [str(i) + ' sets' for i in range(2,match.Rules['SETS_TO_WIN']+1)]
    y_labels[-1] = 'Win!'
    main_ax.set_yticks(y_ticks)
    main_ax.set_yticklabels(y_labels)
    plt.grid(which='major', axis='y')

    main_ax.set_xticks([])

    xlabels = ['0-0']
    current_score=[0,0]
    for set_ in match.Score:
        current_score[set_.Winner]+= 1
        xlabels.append('-'.join(list(map(str, current_score))))

    
    # Create title string using match info
    titlestring = match.PrintPlayers() + '\n' + match.Info['TOURNAMENT'] + ' - ' +match.Info['ROUND'] +'\n' + match.Info['DATE'].isoformat()
    main_ax.set_title(titlestring)

    plt.xlim(0, len(x))
    plt.ylim(score_range[0], score_range[1])
    main_ax.set_xlabel('Match progress')
    main_ax.set_ylabel('\"Victory meter\"')

    main_ax.legend(handles=[mpatches.Patch(color='tab:blue', label=match.Players[0].Last), mpatches.Patch(color='tab:orange', label=match.Players[1].Last)], loc='lower right')
    

    def animate(i):
        j=0
        while i > EoS[j] and j < len(EoS)-1:
            j += 1
        main_ax.axvline(EoS[j-1], linestyle='--', linewidth = 0.3 ,color = 'lightgray')
        main_ax.set_xticks(EoS[:j])
        main_ax.set_xticklabels(xlabels[:j])
        if i >= EoS[-1]:
            main_ax.set_xticks(EoS)
            main_ax.set_xticklabels(xlabels)
        main_ax.plot(x[:i], p1_momentum[:i], color='tab:blue', label=match.Players[0].Last)
        main_ax.plot(x[:i], p2_momentum[:i], color='tab:orange', label=match.Players[1].Last)
        # main_ax.legend(match.Players[0].Last, match.Players[1].Last)
        # main_ax.legend()
        # if i == 0:
        #     main_ax.legend(loc='lower right')
        fig.tight_layout()
        return main_ax
        
    ani = animation.FuncAnimation(fig, animate, frames=len(x)+int(len(x)/5))
    
    

    if save_video:
        outputfilename = match.Players[0].Last + match.Players[1].Last + match.Info['DATE'].isoformat() + '.mp4'
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=20, metadata=dict(artist='TennisMomentumTracker'), bitrate=1800)
        print('Saving animation as {}\nPlease wait...'.format(outputfilename))
        ani.save('outputs/'+outputfilename, writer=writer)
        print('Done!')
    else:
        plt.show()

    return 0


