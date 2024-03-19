$(function () {

    const $container = $('.highlight-product-layout');
    let $cells = $('.cell-item');
    const numVisibleCells = 5; // Số lượng cell hiển thị trên màn hình
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
            $('#prevBtn').hide(); // Ẩn nút prev nếu ở đầu danh sách
        } else {
            $('#prevBtn').show();
        }
        if (currentIndex + numVisibleCells >= $cells.length) {
            $('#nextBtn').hide(); // Ẩn nút next nếu ở cuối danh sách
        } else {
            $('#nextBtn').show();
        }
    }

    $('#prevBtn').click(function () {
        if (currentIndex > 0) {
            currentIndex --; // Di chuyển currentIndex về trước
            updateVisibility();
        }
    });

    $('#nextBtn').click(function () {
        if (currentIndex + numVisibleCells < $cells.length) {
            currentIndex ++; // Di chuyển currentIndex về sau
            updateVisibility();
        }
    });

    // Gọi hàm cập nhật hiển thị ban đầu
    updateVisibility();

});
