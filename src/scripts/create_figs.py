"""
create_figs.py
==============
Orchestrator script to create all the figures
"""

import subprocess

SCRIPT_ARGUMENTS = {
    "create_fig_tsneembedding.py": 1,
    "create_fig_tsneclustering.py": 2,
    "create_fig_coaddedspectrum.py": 3,
    "create_fig_classes.py": [4, 5, 6],
    "create_fig_upset.py": 7,
    "create_fig_whytwoislands.py": 8,
    "create_fig_clustercomparison.py": 9,
}


def main():
    for script, figure_number in SCRIPT_ARGUMENTS.items():
        # Handle multiple arguments
        if isinstance(figure_number, list):
            print(f"Creating figures: {', '.join(map(str, figure_number))}...")
            subprocess.run(["python", script] + [str(fig) for fig in figure_number])
        else:
            print(f"Creating figure {figure_number}...")
            subprocess.run(["python", script, str(figure_number)])


if __name__ == "__main__":
    main()
