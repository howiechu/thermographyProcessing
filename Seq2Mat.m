clear all 
close all
clc

% load file
file = 'D:\Users\engs1560\Documents\ResearchIR Data\KKMB\SOH95\Other\KKMB-3c_fulldschrg_031220-000001.seq';
v = FlirMovieReader([file]);
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
basedir = 'D:\Users\engs1560\Documents\Processed Lock-in\KKMB\SOH95\Other\';
newfolder = 'KKMB_3c_fulldschrg_031220';
mkdir(basedir, newfolder),

%%
% Save the array for processing in python
save([basedir newfolder  '\A.mat'],'A')

%%
% Save timestamps of each frame of IR video to .csv
timeIR = permute(timeIR,[2,1]);
T = cell2table(timeIR);
writetable(T,[basedir newfolder '\timestamps.csv'],'WriteVariableNames',false)

%%
% Test image from mat array
imagesc(A(:,:,1000))