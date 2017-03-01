<html>
    <head>
        <link href="https://fonts.googleapis.com/css?family=Ubuntu" rel="stylesheet">
        <script
          src="https://code.jquery.com/jquery-3.1.1.js"
          integrity="sha256-16cdPddA6VdVInumRGo6IbivbERE8p7CQR3HzTBuELA="
          crossorigin="anonymous">
        </script>
        <style>
            body {
                margin: 0px;
                font-family: 'Ubuntu', sans-serif;
                font-size: 40pt;

                /* Permalink - use to edit and share this gradient: http://colorzilla.com/gradient-editor/#ffffff+0,b7b7b7+79&1+0,0+100 */
                background: -moz-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%, rgba(183,183,183,0.21) 79%, rgba(183,183,183,0) 100%); /* FF3.6-15 */
                background: -webkit-radial-gradient(center, ellipse cover,  rgba(255,255,255,1) 0%,rgba(183,183,183,0.21) 79%,rgba(183,183,183,0) 100%); /* Chrome10-25,Safari5.1-6 */
                background: radial-gradient(ellipse at center,  rgba(255,255,255,1) 0%,rgba(183,183,183,0.21) 79%,rgba(183,183,183,0) 100%); /* W3C, IE10+, FF16+, Chrome26+, Opera12+, Safari7+ */
                filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#00b7b7b7',GradientType=1 ); /* IE6-9 fallback on horizontal gradient */
            }

            .container {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 90%;
            }

            .generate_container {
                position: absolute;
                bottom: 30%;
                width: 100%;
            }

            .button {
                color: white;
                border-radius: 4px;
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
                background: rgb(202, 60, 60);
                border: none;
                font-size: 40pt;
                display: block;
                margin: auto;
                cursor: pointer;
            }

            .button:disabled {
                background: rgb(160, 160, 160);
                cursor: wait;
            }

            .spinner {
              width: 40px;
              height: 40px;

              position: relative;
              margin: 100px auto;
            }

            .double-bounce1, .double-bounce2 {
              width: 100%;
              height: 100%;
              border-radius: 50%;
              background-color: #333;
              opacity: 0.6;
              position: absolute;
              top: 0;
              left: 0;

              -webkit-animation: sk-bounce 2.0s infinite ease-in-out;
              animation: sk-bounce 2.0s infinite ease-in-out;
            }

            .double-bounce2 {
              -webkit-animation-delay: -1.0s;
              animation-delay: -1.0s;
            }

            @-webkit-keyframes sk-bounce {
              0%, 100% { -webkit-transform: scale(0.0) }
              50% { -webkit-transform: scale(1.0) }
            }

            @keyframes sk-bounce {
              0%, 100% {
                transform: scale(0.0);
                -webkit-transform: scale(0.0);
              } 50% {
                transform: scale(1.0);
                -webkit-transform: scale(1.0);
              }
            }
        </style>
    </head>
    <div class="container">
        <div id="haiku" style="display:none"></div>
        <div class="spinner" id="spinner">
          <div class="double-bounce1"></div>
          <div class="double-bounce2"></div>
        </div>
    </div>
    <div class="generate_container">
        <button class="button" id="button" disabled>Generate Haiku</button>
    </div>
    <script>
        function get_haiku() {
            $("#haiku").hide();
            $("#spinner").show();
            $("#button").prop("disabled", true);

            $.get('haiku', function(data) {
                $("#haiku").html(data.haiku).show();
                $("#spinner").hide();
                $("#button").prop("disabled", false);
            });
        }

        $(function() {
            get_haiku();

            $("#button").click(get_haiku);
        });
    </script>
<html>
