$(function () {
    var searchData = {};
    $('input[name="daterange"]').daterangepicker({
        opens: 'left',
        locale: {
            format: 'MMM D, YYYY'
        }
    }, function (start, end, label) {
        searchData['start'] = start ? start.format('YYYY-MM-DD') : undefined;
        searchData['end'] = end ? end.format('YYYY-MM-DD') : undefined;
        searchData['page'] = 1;
        console.log(searchData);
    });


    $("button[name='search']").click(function () {
        const inputSearch = $("input[name='search']").val();
        searchData['search'] = inputSearch || undefined;
        searchData['page'] = 1;
        console.log(searchData);
    })

    $("button[name='sort']").click(function () {
        const sortValue = $(this).val();
        searchData['sort'] = sortValue || undefined;
        searchData['page'] = 1;
        console.log(searchData);
    })

    $("button[name='filter']").click(function () {
        const filterValue = $(this).val();
        searchData['filter'] = filterValue || undefined;
        searchData['page'] = 1;
        console.log(searchData);
    })

    $("button[name='pagination']").click(function () {
        const page = $(this).val();
        if (!isNaN(+page)) {
            const pageLength = $('.page-item').length;

            $('.page-item.active').removeClass('active');
            $($(this)[0].parentElement).addClass('active');
            searchData['page'] = page;
        }
        if (page === 'plus') {
            const oldPage = $('.page-item.active button').val();
            $('.page-item.active').removeClass('active');
            $($(`.page-item button[value='${+oldPage + 1}'`)[0].parentElement).addClass('active');
            searchData['page'] = +oldPage + 1;
        } else if (page === 'minus') {
            const oldPage = $('.page-item.active button').val();
            $('.page-item.active').removeClass('active');
            $($(`.page-item button[value='${+oldPage - 1}'`)[0].parentElement).addClass('active');
            searchData['page'] = +oldPage - 1;
        }
        showPagination();
        const pageLength = $('.page-item').length;
        $('.page-item-minus button').prop('disabled', pageLength <= 1 || +$('.page-item.active button').val() === 1);
        $('.page-item-plus button').prop('disabled', pageLength <= 1 || +$('.page-item.active button').val() === pageLength);
    })

    $('button.btn-detail').click(function () {
        const id = $(this).data('id');
        const status = $(this).data('status');
        let statusText = '';
        switch (status) {
            case 'success':
                statusText = '<i class="bi bi-check-lg"></i>Hoàn Thành';
                $("#detailModal .card-detail-footer .btn-delete").hide();
                break;
            case 'processing':
                statusText = '<i class="bi bi-clock-history"></i>Đang xử lý';
                $("#detailModal .card-detail-footer .btn-delete").show();
                break;
            case 'cancel':
                statusText = '<i class="bi bi-x-lg"></i>Từ chối';
                $("#detailModal .card-detail-footer .btn-delete").show();
                break;
            default:
                statusText = '';
                break
        }
        const removeClass = $("#detailModal .chip-status")[0].classList[1];
        if (removeClass) {
            $("#detailModal .chip-status")[0].classList.remove(removeClass)
        }
        $("#detailModal .chip-status").addClass(`chip-status ${status}`);
        $("#detailModal .chip-status").html(statusText);

        if (discount) {
            $("#detailModal #discount").text(formatNumber(14878500, 'đ'));
            $('#discountContainer').show();
        } else {
            $('#discountContainer').hide()
        }

        $("#detailModal #requiredTime").text('21:02 - 06/12/2024');
        $("#detailModal #finishTime").text('21:02 - 06/12/2024');
        $("#detailModal #quantity").text(formatNumber(66570000));
        $("#detailModal #subtotal").text(formatNumber(66570000, 'đ'));
        $("#detailModal #vat").text(formatNumber(28269150, 'đ'));
        $("#detailModal #total").text(formatNumber(60960650, 'đ'));
        $("#detailModal .card-detail-footer .btn-delete").attr("data-id", id);
        $('#detailModal .card-detail-body.product').append(`
            <div class="d-flex card-detail-product-container">
                <img src="./img.png" class="card-detail-img" alt="" width="128" height="128"
                    height="100px">
                <div class="card-detail-info">
                    <span class="card-detail-product-name">
                        13-inch MacBook Air Space Grey
                        <span class="card-detail-product-quantity">x3</span>
                    </span>
                    <div class="card-detail-product-subtitle">
                        <span>RAM: 16gb</span>
                        <span>Bộ nhớ: 256gb</span>
                        <span>Màu: Đen</span>
                    </div>
                </div>
                <div class="card-detail-product-price">
                    <span class="card-detail-product-price-total">114,450,000₫</span>
                    <span class="card-detail-product-price-unitprice">22,890,000₫/cái</span>
                </div>
            </div>
            `)
    });

    $("#detailModal .card-detail-footer .btn-delete, .btn-remove.dropdown-item").click(function () {
        const id = $(this).data('id')
    })

    $(document).ready(function () {
        showPagination()
    })

    function formatNumber(number, currency) {
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (currency || '')
    }

    function showPagination() {
        const currentPage = +$('.page-item.active button').val();
        const pageLength = $('.page-item').length;
        if (pageLength < 2) {
            $('.btn-pagination-arrow.page-link').prop('disabled', true)
        }
        $('.page-item-more-first')?.show()
        $('.page-item-more-last')?.show()

        $('.page-item').each((i, e) => {
            if (i !== 0 && i !== pageLength - 1) {
                $(e).hide();
            }
            if (currentPage > 3 && currentPage < length - 3) {
                if (i >= currentPage - 2 && i <= currentPage + 2) {
                    $(e).show();
                }
            } else if (currentPage >= pageLength - 3) {
                $('.page-item-more-last')?.hide()
                if (i > pageLength - 5) {
                    $(e).show();
                }
            } else {
                if (i < 6) {
                    $('.page-item-more-first')?.hide()
                    $(e).show();
                }
            }
        })
    }

    // use after call get api (not pagging)
    function backToFirstPage() {
        $('.page-item.active').removeClass('active');
        $($(`.page-item button[value='1']`)[0].parentElement).addClass('active');
    }

    function generatePagination(length) {
        const previousBtn = `<li class="page-item-minus me-auto"><button name="pagination" value="minus"
                                                class="btn btn-pagination-arrow page-link" disabled><i
                                                    class="bi bi-arrow-left-short"></i>Trang trước</button></li>`
        const nextBtn = `<li class="page-item-plus ms-auto"><button name="pagination" value="plus"
                                                class="btn btn-pagination-arrow page-link">Trang kế<i
                                                    class="bi bi-arrow-right-short"></i></button></li>`
        let listPage = ''
        for (var i = 0; i < length; i++) {
            if (i === length - 1) {
                listPage = length > 7 && `<li class="page-item-more-first"><span class="btn-number">...</span></li>` + listPage;
            }
            listPage += `<li class="page-item active"><button name="pagination" value="${i + 1}"
                class="btn-number page-link">${i + 1}</button></li>`
            if (i === 0 && length > 7) {
                listPage += `<li class="page-item-more-last"><span class="btn-number">...</span></li>`;
            }
        }
        const newListPage = previousBtn + listPage + nextBtn;
        $('ul.pagination').empty().append(newListPage);
        showPagination();
    }

});
