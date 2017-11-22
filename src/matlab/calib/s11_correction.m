function s11_correction(folder)

clc
%addpath('/media/DATA/EDGES_codes/edges_mfiles/')


%%%% paths %%%%
folder_mfiles = '/media/DATA/EDGES_codes/edges_mfiles/';
folder_data   = ['/media/DATA/s11/antenna_s11/tuning_january_2015/' folder '/'];
folder_save   = '/media/DATA/s11/antenna_s11/tuning_january_2015/plots/';
folder_calibrated = '/media/DATA/s11/antenna_s11/tuning_january_2015/calibrated/';


%%%% identifying file names %%%%
cd(folder_data)
dir_temp     = dir('voltage_*.txt');
dir_open     = dir('*input1*.s1p');
dir_short    = dir('*input2*.s1p');
dir_load     = dir('*input3*.s1p');
dir_antenna  = dir('*input4*.s1p');
cd(folder_mfiles)

name_temp     = [folder_data dir_temp.name];
name_open     = [folder_data dir_open.name];
name_short    = [folder_data dir_short.name];
name_load     = [folder_data dir_load.name];
name_antenna  = [folder_data dir_antenna.name];


%%%% loading temperature and humidity %%%%
[Tb, Hw, Tw] = temperature_humidity_deployment_2014(name_temp);


%%%% loading S11 data %%%%
open_raw     = s11read(name_open);
short_raw    = s11read(name_short);
load_raw     = s11read(name_load);
antenna_raw  = s11read(name_antenna);


%%%% correcting antenna data %%%%
or =  1*ones(151,1);
sr = -1*ones(151,1);
lr =  0*ones(151,1);
antenna_corr1 = de_embed(or, sr, lr, open_raw, short_raw, load_raw, antenna_raw);
antenna_corr2 = s11_correction_step1(antenna_corr1);
antenna_corr3 = s11_correction_step2(Tb, antenna_corr2);


%%%% saving calibrated trace %%%%
f = [50:1:200]';
sav = [f real(antenna_corr3) imag(antenna_corr3)];
save([folder_calibrated 'calibrated_' folder '.txt'],'sav','-ascii','-double');


%%%% plotting %%%%
close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 10 4]);

subplot(1,2,1)
plot(f,20*log10(abs(antenna_corr3)))
xlabel('frequency [MHz]')
ylabel('magnitude [dB]')
xlim([100 200])
set(gca,'ytick',-20:1:0)
ylim([-20 0])
grid

subplot(1,2,2)
plot(f,(180/pi)*unwrap(angle(antenna_corr3)))
xlabel('frequency [MHz]')
ylabel('phase [degrees]')
xlim([100 200])
grid

print(fig, '-dpng', [folder_save 'plot_' folder '.png']);



