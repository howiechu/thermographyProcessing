clear all 
close all
clc

% load file
file = 'path_to_file';
v = FlirMovieReader(file);
v.unit = 'temperatureFactory';

%%
% initialize array with video properties
vidInfo = info(v);
A = zeros(vidInfo.height,vidInfo.width,vidInfo.numFrames-1);
timeIR = cell(1,vidInfo.numFrames-1);

%%
% assemble frames into the array
for i = 1:vidInfo.numFrames-1
    A(:,:,i) = step(v,i);
    ts = getMetaData(v);
    timeIR{i} = ts.Time;
end

%%
% Create a new directory for processed data
dir = 'path_of_new_directory';
mkdir(dir),

%%
% Save the array for processing in python
save([dir '\A.mat'],'A')

%%
% Save timestamps of each frame of IR video to .csv
timeIR = permute(timeIR,[2,1]);
T = cell2table(timeIR);
writetable(T,[dir '\timestamps.csv'],'WriteVariableNames',false)

%%
% Test image from mat array
imagesc(A(:,:,1000))