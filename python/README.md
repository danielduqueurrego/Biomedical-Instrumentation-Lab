# Python acquisition tools

This folder contains the shared Python acquisition code plus student-facing launchers.

## Layout
- `acquisition/`: shared protocol, preset, serial, logging, and plotting helpers
- `apps/`: student-facing apps built from the shared acquisition helpers
- `run_*.py`: simple entry points for each app
- `launch_*.sh` and `launch_*.bat`: beginner-friendly launcher scripts

## Minimal setup
1. Install a free Conda-based Python distribution such as Miniconda or Anaconda.
2. Open a terminal in this `python` folder.
3. Create the environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`

## Current baseline app
The first reference app is a `CONT_MED` three-channel demo for Arduino UNO R4 WiFi.

Run it from this folder with:
- `python run_cont_med_three_channel.py`
- `python run_cont_med_three_channel.py --port COM3`
- `./launch_cont_med_three_channel.sh`
- `launch_cont_med_three_channel.bat --port COM3`

If only one serial port is present, the app can auto-select it. If several ports are present, use `--port`.

## Output files
The reference app saves one session folder under:
- `../data/cont_med/three_channel_data_demo/<timestamp>/`

That session folder contains:
- `data_samples.csv`
- `metadata.csv`
- `parse_errors.log`

Close the plot window to stop acquisition.
