function folds = compressFolds(folds)

    for i = 1:length(folds)
        % PCA to 95% variance explained
        display(sprintf('Compressing fold %2d', i));
        [C, spectrum] = pca(folds(i).Ktrain');
        dim = find(cumsum(spectrum) >= 0.95 * sum(spectrum), 1);
        C = C(:,1:dim);
        
        folds(i).Ktrain         = C' * folds(i).Ktrain;
        folds(i).Kvalidation    = C' * folds(i).Kvalidation;
        folds(i).Ktest          = C' * folds(i).Ktest;
        folds(i).C              = C;

    end
end

function [C, spectrum] = pca(X)

    [C, spectrum] = eig(cov(X));
    [spectrum, I] = sort(diag(spectrum), 'descend');
    C = C(:,I);
end
