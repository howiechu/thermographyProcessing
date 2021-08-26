# Code to process IR video from FLIR cameras

Converts FLIR .seq files to .mat files using Flir's [Science File SDK](https://flir.custhelp.com/app/account/fl_download_software) (matlab code)
- Requires 
    - FlirMovieReader.m
    - FlirMovieReaderMex.mexw64
    - fnv.dll
    - fnvfile.dll
    - fnvreduce.dll
    - CharLS.dll
    - sqlite3.dll (Windows)
    - zlib1.dll (Windows)
- Seq2Mat.m : script for converting the seq video files
- Convert_Single_Frames.m : does the same from a timelapse like capture method where each .seq file only has 1 frame

Processes the resulting .mat files for input into this [electrochemical/thermal model](https://github.com/howiechu/lock-in-thermography-model) from this [paper](https://doi.org/10.1016/j.jpowsour.2020.227787).
- FLIR_Ivium : syncs IR video data with IVIUM sqlite files 
- FlIR_Kepco : syncs IR video data with Data Translation DT9829-8 DAQ box; Kepco power supply was used to apply currents for experiments