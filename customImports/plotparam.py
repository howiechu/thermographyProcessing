import matplotlib.pyplot as plt
from matplotlib import rc, font_manager

thermography_pastel = ['#f97068','#17c3b2','#002147','#912F56']

def update_params():
    tick_size = 12
    fontlabel_size = 12
    params = {
        'backend': 'wxAgg',
        # 'lines.marker': 'o',
        'lines.markersize': 1,
        'lines.antialiased': True,
        'axes.labelsize': fontlabel_size,
        'font.size': fontlabel_size,
        'legend.fontsize': fontlabel_size,
        'xtick.labelsize': tick_size,
        'xtick.direction': 'in',
        'xtick.top': True,
        'ytick.labelsize': tick_size,
        'ytick.direction': 'in',
        'ytick.right': True,
        'font.family': 'Times',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    }
    plt.rcParams.update(params)
    