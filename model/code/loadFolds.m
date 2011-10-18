function folds = loadFolds(path)

    d = dir(path);


    j = 1;
    for i = 1:length(d)
        
        if strncmp(d(i).name, '.', 1)
            continue;
        end
        folds(j) = loadFold([path, '/', d(i).name]);
        j = j + 1;
    end
end


function fold = loadFold(path)

    fold = struct( ...
                    'test_names',   [], ...
                    'test_artists', [], ...
                    'test_Y',       [], ...
                    'Ktest',        [], ...
                    'validation_names',   [], ...
                    'validation_artists', [], ...
                    'validation_Y',       [], ...
                    'Kvalidation',        [], ...
                    'train_names',   [], ...
                    'train_artists', [], ...
                    'train_Y',       [], ...
                    'Ktrain',        []);

    splits = {'train', 'validation'};
    textdata = {'names', 'artists'};
    for i = 1:length(splits)
        for j = 1:length(textdata)
            fold = setfield(   fold, ...
                        sprintf('%s_%s', splits{i}, textdata{j}), ...
                        loadTextData(sprintf('%s/%s_%s', path, splits{i}, textdata{j})));
        end

        fold = setfield(   fold, ...
                    sprintf('K%s', splits{i}), ...
                    importdata(sprintf('%s/%s_data_vector', path, splits{i}))');

        fold = setfield(   fold, ...
                    sprintf('%s_Y', splits{i}), ...
                    loadConstraints(sprintf('%s/%s_Y', path, splits{i})));
    end
end

function D = loadTextData(filename)

    fid = fopen(filename, 'r');
    D   = textscan(fid, '%[^\n]\n');
    D = D{1};
    fclose(fid);
end

function Y = loadConstraints(filename)

    R = dlmread(filename, ',');

    Y = cell(size(R,1), 1);
    for i = 1:length(Y)
        Y{i} = R(i, find(R(i,:) > 0))';
    end
end
