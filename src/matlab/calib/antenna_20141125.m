
clear all
close all
clc

addpath('/data2/raul/EDGES/calibration/antenna/front_end_calibration/mfiles/')


%%%% LOADING AND CORRECTING DATA %%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%% paths %%%%
folder_mfiles = '/data2/raul/EDGES/calibration/antenna/field_antenna_s11/mfiles/';
folder_data   = '/data2/raul/EDGES/calibration/antenna/field_antenna_s11/data/raw/20141125/';
folder_save   = '/data2/raul/EDGES/calibration/antenna/field_antenna_s11/data/corrected/20141125/';
cd(folder_mfiles)


%%%% temperature and humidity at each measurement %%%%
[Tb, Hw, Tw]    = temperature_humidity_deployment_2014([folder_data 'voltage_20141125_145417.txt']);



%%%% listing files %%%%
cd(folder_data)
input1 = dir('*input1*.s1p');
input2 = dir('*input2*.s1p');
input3 = dir('*input3*.s1p');
input4 = dir('*input4*.s1p');
   
cd(folder_mfiles)
l = min([length(input1) length(input2) length(input3) length(input4)]);

%%%% correction of measurements %%%%
open_m  = [];
short_m = [];
match_m = [];
load_m  = [];
load_c  = [];
load_cc = [];
load_ccc = [];

s11    = [];
s12s21 = [];
s22    = [];

for i = 1:l
    disp(i)
    
    %%%% file names %%%%
    n1 = input1(i).name;
    n2 = input2(i).name;
    n3 = input3(i).name;
    n4 = input4(i).name;
       
    %%%% measured s11 traces %%%%
    open_t  = s11read([folder_data n1]);
    short_t = s11read([folder_data n2]);
    match_t = s11read([folder_data n3]);
    load_t  = s11read([folder_data n4]);
    
    open_m(:,i)  = open_t;
    short_m(:,i) = short_t;
    match_m(:,i) = match_t;
    load_m(:,i)  = load_t;
    
    %%%% correction %%%%
    or =  1*ones(151,1);
    sr = -1*ones(151,1);
    mr =  0*ones(151,1);
    [load_c(:,i) s11(:,i) s12s21(:,i) s22(:,i)] = de_embed(or, sr, mr, open_t, short_t, match_t, load_t);
    load_cc(:,i)  = s11_correction_step1(load_c(:,i));
    load_ccc(:,i) = s11_correction_step2(Tb(i), load_cc(:,i));
    
end

data_all = cell(1,2);
data_all{1,1} = load_ccc;
data_all{1,2} = [Tb Hw Tw];


%save([folder_save 'corrected_s11.mat'],'data_all','-mat')


%% plotting %%
index_vector = 0:200;
data         = data_all{1};




close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);

subplot(3,1,1)
plot(index_vector, Tw, 'k.-')
hold
plot(index_vector, Tb, 'r.-')
%xlim([0 4])
ylim([10 50])
%xlabel('time [hrs]')
ylabel('temperature [ ^oC]')
legend('ambient','switch')



subplot(3,1,2)
plot(index_vector, Hw, 'k.-')
xlim([0 200])
ylim([-50 110])
ylabel('relative humidity [%]')


subplot(3,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(data)))
caxis([-20 -10])
%xlim([0 4])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude S_{11}: Antenna Corrected')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/summary_antenna_corrected.eps']);







%% 
index_vector = 0:200;
data         = data_all{1};




close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);

subplot(3,1,1)
plot(index_vector, Tw, 'k.-')
hold
plot(index_vector, Tb, 'r.-')
%xlim([0 4])
ylim([10 50])
%xlabel('time [hrs]')
ylabel('temperature [ ^oC]')
legend('ambient','switch')



subplot(3,1,2)
plot(index_vector, Hw, 'k.-')
xlim([0 200])
ylim([-50 110])
ylabel('relative humidity [%]')


subplot(3,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(open_m)))
%caxis([-20 -10])
%xlim([0 4])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude S_{11}: Open Measured')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/summary_open_measured.eps']);


%%
index_vector = 0:200;
data         = data_all{1};




close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);

subplot(3,1,1)
plot(index_vector, Tw, 'k.-')
hold
plot(index_vector, Tb, 'r.-')
%xlim([0 4])
ylim([10 50])
%xlabel('time [hrs]')
ylabel('temperature [ ^oC]')
legend('ambient','switch')



subplot(3,1,2)
plot(index_vector, Hw, 'k.-')
xlim([0 200])
ylim([-50 110])
ylabel('relative humidity [%]')


subplot(3,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(short_m)))
%caxis([-20 -10])
%xlim([0 4])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude S_{11}: Short Measured')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/summary_short_measured.eps']);



%%
index_vector = 0:200;
data         = data_all{1};




close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);

subplot(3,1,1)
plot(index_vector, Tw, 'k.-')
hold
plot(index_vector, Tb, 'r.-')
%xlim([0 4])
ylim([10 50])
%xlabel('time [hrs]')
ylabel('temperature [ ^oC]')
legend('ambient','switch')



subplot(3,1,2)
plot(index_vector, Hw, 'k.-')
xlim([0 200])
ylim([-50 110])
ylabel('relative humidity [%]')


subplot(3,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(match_m)))
caxis([-100 -10])
%xlim([0 4])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude S_{11}: Match Measured')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/summary_match_measured.eps']);



%%
index_vector = 0:200;
data         = data_all{1};




close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);

subplot(3,1,1)
plot(index_vector, Tw, 'k.-')
hold
plot(index_vector, Tb, 'r.-')
%xlim([0 4])
ylim([10 50])
%xlabel('time [hrs]')
ylabel('temperature [ ^oC]')
legend('ambient','switch')



subplot(3,1,2)
plot(index_vector, Hw, 'k.-')
xlim([0 200])
ylim([-50 110])
ylabel('relative humidity [%]')


subplot(3,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(load_m)))
%caxis([-100 -10])
%xlim([0 4])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude S_{11}: Antenna Measured')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/summary_antenna_measured.eps']);


%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 10 8]);

subplot(5,1,1)
imagesc(index_vector, 50:1:200, 20*log10(abs(open_m))-repmat(20*log10(abs(open_m(:,1))),1,201))
ylim([100 200])
cb = colorbar;
caxis([-1 1])
ylabel('[MHz]')
ylabel(cb,'[dB]')
title('\Delta Open Measured')
set(gca,'xticklabel',[])

subplot(5,1,2)
imagesc(index_vector, 50:1:200, 20*log10(abs(short_m))-repmat(20*log10(abs(short_m(:,1))),1,201))
ylim([100 200])
cb = colorbar;
caxis([-1 1])
ylabel('[MHz]')
ylabel(cb,'[dB]')
title('\Delta Short Measured')
set(gca,'xticklabel',[])

subplot(5,1,3)
imagesc(index_vector, 50:1:200, 20*log10(abs(match_m))-repmat(20*log10(abs(match_m(:,1))),1,201))
ylim([100 200])
cb = colorbar;
caxis([-5 5])
ylabel('[MHz]')
ylabel(cb,'[dB]')
title('\Delta Match Measured')
set(gca,'xticklabel',[])

subplot(5,1,4)
imagesc(index_vector, 50:1:200, 20*log10(abs(load_m))-repmat(20*log10(abs(load_m(:,1))),1,201))
ylim([100 200])
cb = colorbar;
caxis([-5 5])
ylabel('[MHz]')
ylabel(cb,'[dB]')
title('\Delta Antenna Measured')
set(gca,'xticklabel',[])

subplot(5,1,5)
imagesc(index_vector, 50:1:200, 20*log10(abs(load_ccc))-repmat(20*log10(abs(load_c(:,1))),1,201))
ylim([100 200])
cb = colorbar;
caxis([-5 5])
xlabel('time [Hr]')
ylabel('[MHz]')
ylabel(cb,'[dB]')
title('\Delta Antenna Corrected')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/deltas.eps']);


%%





for i = 1:151
    
    if i > 50
    
    close all
    fig=figure('visible','off');
    set(fig, 'PaperPosition', [0 0 4 3]);
    
    
    
    
    subplot(2,1,1)
    mag1 = 20*log10(abs(load_ccc(i,39:82)));
    mag2 = 20*log10(abs(load_ccc(i,115:end)));
    
    plot(Tw(39:82),mag1,'.')
    hold
    plot(Tw(115:end),mag2,'r.')
    ylabel('magnitude S_{11} [dB]')
    title([num2str(i+49) ' MHz'])
    
    
    
    
    subplot(2,1,2)
    ang1 = (180/pi)*unwrap(angle(load_ccc(i,39:82)));
    ang2 = (180/pi)*unwrap(angle(load_ccc(i,115:end)));
    
    if (min(ang1) > 100) && (max(ang2) < -100)
        ang1 = ang1 - 360;
    elseif (min(ang2) > 100) && (max(ang1) < -100)
        ang2 = ang2 - 360;
    end
    
    
    plot(Tw(39:82),ang1,'.')
    hold
    plot(Tw(115:end),ang2,'r.')
    xlabel('ambient temperature [ ^oC]')
    ylabel('phase S_{11} [ ^o]')
     
    
    print(fig, '-dpng', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/correlations1/freq_' num2str(i+49) '_MHz.png']);
    
    end
end

%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 6 6]);


p1 = subplot(2,1,1);
plot(0:46,Tw(39:85),'.k-','markersize',10)
xlim([0 46])
ylabel('ambient temperature [ ^oC]')

p2 = subplot(2,1,2);
imagesc(0:46,50:200,20*log10(abs(data(:,39:85))));ylim([100 200]);caxis([-20 -14])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude Antenna S_{11}')
cb = colorbar;
ylabel(cb,'[dB]')
xlim([0 46])



x0 = 0.1;
y0 = 0.1;
dx = 0.75;
dy = 0.35;
xoff = 0;
yoff = 0.14;

set(p1,'position',[x0, y0+yoff+dy, dx, dy])
set(p2,'position',[x0, y0, dx, dy])


print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section1.eps']);






%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 6 4]);


plot(50:200,20*log10(abs(data(:,39:85))),'g')
hold
plot(50:200,20*log10(abs(data(:,42))),'r')
plot(50:200,20*log10(abs(data(:,79))),'b')
xlim([100 200])
xlabel('frequency   [MHz]')
ylabel('magnitude  S_{11}   [dB]')
grid



print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section1_all.eps']);


%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 8 5]);



subplot(3,2,1)
plot(Tw(39:85), 20*log10(abs(data(74,39:85))),'.','markersize',10)
title('MAGNITUDE   S_{11}','fontsize',14)
ylabel('[dB]')
xlim([24 38])
text(34.5,-16.5,'120 MHz','fontweight','bold')
set(gca,'xticklabel',[])


subplot(3,2,3)
plot(Tw(39:85), 20*log10(abs(data(100,39:85))),'.','markersize',10)
ylabel('[dB]')
xlim([24 38])
%ylim([-17.5 -16])
text(34.5,-16.4,'140 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,5)
plot(Tw(39:85), 20*log10(abs(data(125,39:85))),'.','markersize',10)
ylabel('[dB]')
xlabel('ambient temperature [ ^oC]')
xlim([24 38])
text(34.5,-17.9,'160 MHz','fontweight','bold')



subplot(3,2,2)
plot(Tw(39:85), (180/pi)*unwrap(angle(data(75,39:85))),'.','markersize',10)
title('PHASE   S_{11}','fontsize',14)
ylabel('[degrees]')
xlim([24 38])
text(34.5,176,'120 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,4)
plot(Tw(39:85), (180/pi)*unwrap(angle(data(90,39:85))),'.','markersize',10)
ylabel('[degrees]')
xlim([24 38])
text(34.5,59,'140 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,6)
plot(Tw(39:85), (180/pi)*unwrap(angle(data(110,39:85))),'.','markersize',10)
ylabel('[degrees]')
xlabel('ambient temperature [ ^oC]')
xlim([24 38])
text(34.5,-87,'160 MHz','fontweight','bold')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section1_correlations.eps']);




%%

%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 6 6]);


p1 = subplot(2,1,1);
plot(0:85,Tw(115:200),'.k-','markersize',10)
xlim([0 85])
ylabel('ambient temperature [ ^oC]')

p2 = subplot(2,1,2);
imagesc(0:85,50:200,20*log10(abs(data(:,115:200))));ylim([100 200]);caxis([-20 -14])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('Magnitude Antenna S_{11}')
cb = colorbar;
ylabel(cb,'[dB]')
xlim([0 85])



x0 = 0.1;
y0 = 0.1;
dx = 0.75;
dy = 0.35;
xoff = 0;
yoff = 0.14;

set(p1,'position',[x0, y0+yoff+dy, dx, dy])
set(p2,'position',[x0, y0, dx, dy])


print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section2.eps']);






%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 6 4]);


plot(50:200,20*log10(abs(data(:,39:85))),'g')
hold
plot(50:200,20*log10(abs(data(:,42))),'r')
plot(50:200,20*log10(abs(data(:,79))),'b')
xlim([100 200])
xlabel('frequency   [MHz]')
ylabel('magnitude  S_{11}   [dB]')
grid



print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section2_all.eps']);


%%

close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 8 5]);



subplot(3,2,1)
plot(Tw(115:200), 20*log10(abs(data(75,115:200))),'.','markersize',10)
title('MAGNITUDE   S_{11}','fontsize',14)
ylabel('[dB]')
xlim([24 38])
text(34.5,-16.5,'120 MHz','fontweight','bold')
set(gca,'xticklabel',[])


subplot(3,2,3)
plot(Tw(115:200), 20*log10(abs(data(100,115:200))),'.','markersize',10)
ylabel('[dB]')
xlim([24 38])
%ylim([-17.5 -16])
text(34.5,-16.4,'140 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,5)
plot(Tw(115:200), 20*log10(abs(data(125,115:200))),'.','markersize',10)
ylabel('[dB]')
xlabel('ambient temperature [ ^oC]')
xlim([24 38])
text(34.5,-17.9,'160 MHz','fontweight','bold')



subplot(3,2,2)
plot(Tw(115:200), (180/pi)*unwrap(angle(data(75,115:200))),'.','markersize',10)
title('PHASE   S_{11}','fontsize',14)
ylabel('[degrees]')
xlim([24 38])
text(34.5,176,'120 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,4)
plot(Tw(115:200), (180/pi)*unwrap(angle(data(100,115:200))),'.','markersize',10)
ylabel('[degrees]')
xlim([24 38])
text(34.5,59,'140 MHz','fontweight','bold')
set(gca,'xticklabel',[])

subplot(3,2,6)
plot(Tw(115:200), (180/pi)*unwrap(angle(data(125,115:200))),'.','markersize',10)
ylabel('[degrees]')
xlabel('ambient temperature [ ^oC]')
xlim([24 38])
text(34.5,-87,'160 MHz','fontweight','bold')

print(fig, '-depsc', ['/data2/raul/EDGES/calibration/antenna/field_antenna_s11/plots/20141125/section2_correlations.eps']);














%%
%%
close all


plot((180/pi)*unwrap(angle(data(:,1))),'.')


%%

close all

subplot(2,1,1)
plot(115:200,Tb(115:200),'.k-')
xlim([115 200])

subplot(2,1,2)
imagesc(115:200,50:200,20*log10(abs(data(:,115:200))));ylim([100 200]);caxis([-20 -14])
xlim([115 200])


%%




close all

plot(Tb(115:200), 20*log10(abs(data(100,115:200))),'.')



% here !!!!!


















%%














ref_mag1 = repmat(20*log10(abs(mean(data(:,1:10).').')), 1, 2949);
ref_mag2 = repmat(20*log10(abs(mean(data(:,2940:2949).').')), 1, 2949);

ref_ang1 = repmat((180/pi)*unwrap(angle(mean(data(:,1:10).').')), 1, 2949);
ref_ang2 = repmat((180/pi)*unwrap(angle(mean(data(:,2940:2949).').')), 1, 2949);





close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);


subplot(2,1,1)
imagesc(time_vector, 50:1:200, 20*log10(abs(data)) - ref_mag1)
caxis([-0.4 0.4])
hc = colorbar;
set(hc,'ytick',[-0.4:0.2:0.4])
ylabel(hc,'[dB]')
xlim([0 50])
ylim([100 200])
%xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('\Delta Magnitude Antenna S_{11}')


subplot(2,1,2)
imagesc(time_vector, 50:1:200, (180/pi)*unwrap(angle(data)) - ref_ang1)
caxis([-3 3])
hc = colorbar;
set(hc,'ytick',[-3:1:3])
ylabel(hc,'[degrees]')
xlim([0 50])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('\Delta Phase Antenna S_{11}')

print(fig, '-depsc', ['/edges/antenna_s11/field_antenna_s11/plots/20141125/deltas.eps']);





















close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 7 7]);


subplot(2,1,1)
imagesc(time_vector, 50:1:200, 20*log10(abs(data)) - ref_mag1)
caxis([-0.1 0.1])
hc = colorbar;
set(hc,'ytick',[-0.1:0.05:0.1])
ylabel(hc,'[dB]')
xlim([0 32])
ylim([100 200])
%xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('\Delta Magnitude Antenna S_{11}')


subplot(2,1,2)
imagesc(time_vector, 50:1:200, (180/pi)*unwrap(angle(data)) - ref_ang1)
caxis([-1 1])
hc = colorbar;
set(hc,'ytick',[-1:0.5:1])
ylabel(hc,'[degrees]')
xlim([0 32])
ylim([100 200])
xlabel('time [hrs]')
ylabel('frequency [MHz]')
title('\Delta Phase Antenna S_{11}')

print(fig, '-depsc', ['/edges/antenna_s11/field_antenna_s11/plots/20141125/deltas_detail.eps']);



%%


d2 = load('../../field_test_S11/results/test_antenna_tuning/Tues7.txt');
md2 = 20*log10(abs(complex(d2(:,2),d2(:,3))));
ad2 = (180/pi)*unwrap(angle(complex(d2(:,2),d2(:,3))));



close all
fig=figure('visible','off');
set(fig, 'PaperPosition', [0 0 8 5]);

subplot(2,2,1)
plot(50:1:200, ref_mag1(:,1),'b')
hold
plot(50:1:200, ref_mag2(:,1),'r')
xlim([100 200])
ylabel('magnitude [dB]')

subplot(2,2,3)
plot(50:1:200, ref_mag1(:,1) - md2,'b')
hold
plot(50:1:200, ref_mag2(:,1) - md2,'r')
xlim([100 200])
ylabel('\Delta magnitude [dB]')
xlabel('frequency [MHz]')




subplot(2,2,2)
plot(50:1:200, ref_ang1(:,1),'b')
hold
plot(50:1:200, ref_ang2(:,1),'r')
xlim([100 200])
ylabel('phase [degrees]')
legend('beginning','end')



subplot(2,2,4)
plot(50:1:200, ref_ang1(:,1) - ad2,'b')
hold
plot(50:1:200, ref_ang2(:,1) - ad2,'r')
xlim([100 200])
ylabel('\Delta phase [degrees]')
xlabel('frequency [MHz]')







print(fig, '-depsc', ['/edges/antenna_s11/field_antenna_s11/plots/20141125/traces.eps']);


