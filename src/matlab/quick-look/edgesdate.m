function [out] = edgesdate(dvec)

    if (size(dvec) == [1 5])
        dvec = dvec';
    end
    
    out = dvec(1,:) + (dvec(2,:) + (dvec(3,:) + (dvec(4,:) + dvec(5,:) ./ 60) ./ 60) ./ 24) ./ 366;