var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        cart_total_count: 0,
        carts: [],
    },
    mounted() {
        this.get_carts();
    },
    methods: {
        get_carts() {
            let url = '/carts/simple/';
            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for (let i = 0; i < this.carts.length; i++) {
                        if (this.carts[i].name.length > 25) {
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        // 发起支付
        order_payment() {
            var order_id = get_query_string('order_id');
            var url = '/payment/' + order_id + '/';
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // 跳转到支付宝
                        location.href = response.data.alipay_url;
                    } else if (response.data.code == '4101') {
                        location.href = '/login/?next=/orders/info/1/';
                    } else {
                        console.log(response.data);
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});


// $(function () {
//
// });
//
//
// $('.payment').click(function () {
//     var order_id = get_query_string('order_id');
//     var url = '/payment/' + order_id + '/';
//     $.get(url, function (response) {
//         if (response.code == '0') {
//             location.href = response.alipay_url;
//         } else if (response.code == '4101') {
//             location.href = '/login/?next=/orders/info/1/';
//         } else {
//             console.log(response);
//             alert(response.errmsg);
//         }
//     });
// });
