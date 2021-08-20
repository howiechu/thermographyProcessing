clear all 
close all
clc

% Point to directory that contains all the individual .seq files
folder = 'D:\Users\engs1560\Documents\ResearchIR Data\KKMG\100SOH\SOC50\Test\';
list = dir(folder);
list(1:2) = [];

% load a single file to grab video properties
v = FlirMovieReader([folder list(1).name]);
v.unit = 'temperatureFactory';

%%
% Initialize arrays
vidInfo = info(v);
A = zeros(vidInfo.height,vidInfo.width,size(list,1));
timeIR = cell(1,size(list,1));

%%
% Populate arrays
for i = 1:size(list,1)
    w = FlirMovieReader([folder list(i).name]);
    w.unit = 'temperatureFactory';
    A(:,:,i) = read(w);
    ts = getMetaData(w);
    timeIR{i} = ts.Time;
end

%%
% Save file into input directory
save([folder 'A.mat'],'A')

%%
% Save timestamps file
timeIR = permute(timeIR,[2,1]);
T = cell2table(timeIR);
writetable(T,[folder 'timestamps.csv'],'WriteVariableNames',false)

%%
% view single frame 
imagesc(A(:,:,150))