function [residuals, weights, rms, pvals] = fit_polynomial(spec, npoly, rfi_threshold, bKillNeighbors)

    nchannels = length(spec);
    x = (1:nchannels)' .* 2 ./ nchannels - 1.0;
    new_wts = 1;
    old_wts = 0;
    count = 0;
    rms = 0;
        
    % Prime the weights
    weights = ones(nchannels,1);
    
    
    while (((new_wts > old_wts) | (count < 2)) & (count < 40))
          
        count = count + 1;
        old_wts = new_wts;

        good_channels = find(weights==1);
        
        pvals = polyfit(x(good_channels), spec(good_channels), npoly);
        residuals = spec - polyval(pvals, x);
        
        rms = std(residuals .* weights);
        outliers = find(residuals > rms * rfi_threshold);
                
        % Include neighboring channels
        if (bKillNeighbors)
            outliers_all = [outliers, outliers-1, outliers-2, outliers+1, outliers+2];
            outliers_all = outliers_all(find((outliers_all >= 1) & (outliers_all <= nchannels)));
        else
            outliers_all = outliers;
        end
        
        weights = ones(nchannels,1);
        weights(outliers_all) = 0;

        new_wts = nchannels - sum(weights);
        
    end
   
end