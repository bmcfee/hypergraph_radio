function showModel(path)

    load(path, 'A', 'names', 'p');

    name = strrep(path, 'model_', '');

    figure;
    h1 = subplot(1,2,1);
        barh(p, 1), axis ij, title(sprintf('%s - \\pi', name));
        set(gca, 'YTick', 1:size(names,1), 'YTickLabel', names);
        ylim(0.5 + [0 size(names,1)]), xlim([0 1.0]);
        set(gca, 'FontName', 'FreeMono');
        set(gca, 'XGrid', 'on');

    h2 = subplot(1,2,2);
        imagesc(A), axis off, title(sprintf('%s - A', name)), colormap hot;
        set(gca, 'FontName', 'FreeMono');

    fig1pos = get(h1, 'Position');

    fig2pos = get(h2, 'Position');
    fig2pos(1) = fig1pos(1) + fig1pos(3);
    set(h2, 'Position', fig2pos);

end
