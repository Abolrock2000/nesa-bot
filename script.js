document.addEventListener(
    "DOMContentLoaded",
    () => {

        const loadingScreen =
            document.getElementById(
                "loadingScreen"
            );

        const progress =
            document.getElementById(
                "loadingProgress"
            );

        const startButton =
            document.getElementById(
                "startButton"
            );

        const rose =
            document.querySelector(
                ".rose-wrapper"
            );

        const endText =
            document.getElementById(
                "endText"
            );

        let value = 0;

        /*
        ============================================
        Loading
        ============================================
        */

        startButton.disabled = true;

        const loader =
            setInterval(
                () => {

                    value += 2;

                    progress.style.width =
                        value + "%";

                    if (value >= 100) {

                        clearInterval(
                            loader
                        );

                        startButton.disabled =
                            false;
                    }

                },
                35
            );


        /*
        ============================================
        Start
        ============================================
        */

        startButton.addEventListener(
            "click",
            () => {

                loadingScreen.classList.add(
                    "hidden"
                );

                setTimeout(
                    () => {

                        rose.classList.add(
                            "grow"
                        );

                    },
                    500
                );

                setTimeout(
                    () => {

                        rose.classList.add(
                            "bloom"
                        );

                    },
                    2300
                );

                setTimeout(
                    () => {

                        endText.classList.add(
                            "show"
                        );

                        startPetals();

                    },
                    5000
                );

            }
        );


        /*
        ============================================
        Falling petals
        ============================================
        */

        function startPetals() {

            setInterval(
                () => {

                    createPetal();

                },
                650
            );

        }


        function createPetal() {

            const petal =
                document.createElement(
                    "div"
                );

            petal.className =
                "falling-petal";

            petal.style.left =
                Math.random() * 100 + "vw";

            petal.style.animationDuration =
                (5 + Math.random() * 5) + "s";

            petal.style.opacity =
                .4 + Math.random() * .6;

            petal.style.transform =
                `rotate(${Math.random() * 360}deg)`;

            document.body.appendChild(
                petal
            );

            setTimeout(
                () => {

                    petal.remove();

                },
                11000
            );
        }

    }
);
