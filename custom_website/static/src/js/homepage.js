$(function () {

    const $container = $('.highlight-product-layout');
    let $cells = $('.cell-item');
    const numVisibleCells = 5; 
    let currentIndex = 0;

    function updateVisibility() {
        $cells.each(function (index) {
            if (index >= currentIndex && index < currentIndex + numVisibleCells) {
                $(this).removeClass('d-none');
            } else {
                $(this).addClass('d-none');
            }
        });

        if (currentIndex === 0) {
            $('#prevBtn').hide();
        } else {
            $('#prevBtn').show();
        }
        if (currentIndex + numVisibleCells >= $cells.length) {
            $('#nextBtn').hide(); 
        } else {
            $('#nextBtn').show();
        }
    }

    $('#prevBtn').click(function () {
        if (currentIndex > 0) {
            currentIndex --;
            updateVisibility();
        }
    });

    $('#nextBtn').click(function () {
        if (currentIndex + numVisibleCells < $cells.length) {
            currentIndex ++;
            updateVisibility();
        }
    });

    updateVisibility();

});
