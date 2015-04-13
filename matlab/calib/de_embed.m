function [la s11 s12s21 s22] = de_embed(ga1, ga2, ga3, gm1, gm2, gm3, lm)
%
% Raul Monsalve, February 5 2013. Revision, July 17 2013
% 
%
% Usage: out=de_embed(ga1,ga2,ga3,gm1,gm2,gm3,lm)
%
% Inputs are the actual and measured complex reflection coefficients of
% three standard loads. Each vector is a one column complex vector of
% length n. n corresponds to n frequency points. No frequency data is entered 
% to this program.
% 
% Output out is a 3 x n matrix. In descending order, each column contains:
% [S11; S12S21 - S11S22; S22]. There are n columns, one per frequency. 
%


% computing s-parameters
xx=[];
for i=1:length(ga1(:,1))
    b=[gm1(i); gm2(i); gm3(i)];
    A=[1 ga1(i) ga1(i)*gm1(i); 1 ga2(i) ga2(i)*gm2(i); 1 ga3(i) ga3(i)*gm3(i)];
    x=inv(A)*b;
    xx=[xx x];
end



% extracting S-parameters from xx vector
s11=xx(1,:);
s22=xx(3,:);
s12s21=xx(2,:)+s11.*s22;


% transforming them to column vectors 
s11=s11';     
s22=s22';
s12s21=s12s21';


% fixing sign of imaginary part
s11=complex(real(s11),-imag(s11));
s22=complex(real(s22),-imag(s22));
s12s21=complex(real(s12s21),-imag(s12s21));


% corrected reflection coefficient of load
la=(lm-s11)./(s12s21+(lm-s11).*s22);



