// 페이지가 맨 처음 로드 될 때 동작
window.onload = function() {
    // main.html에서 get 형식으로 보낸 정보를 parsing
    var urlParams = new URLSearchParams(window.location.search);
    var selectedContent = urlParams.get('selected');
    var selectedButton = urlParams.get('button')
    var selectedMain = urlParams.get('main')

    // get 형식으로 받은 데이터가 유효하지 않으면 기본값과 함께 홈페이지 이동
    if (!selectedContent || !selectedButton)
    {
        changeActive('top-menu-gangGi')
        showContentLeftMenu('left-menu-gangGi', 'main-content-init-GangGi');
    }

    // get 형식으로 받은 데이터에 맞게 기수 버튼 활성화, 기수 메뉴 노출
    else
    {
        changeActive(selectedButton)
        showContentLeftMenu(selectedContent, selectedMain)
    }

    // get 형식부분 주소창 깔끔하게 지우기
    history.replaceState({}, document.title, window.location.pathname);
};

// 세로모드일 떄 왼쪽 메뉴 토글기능
function toggleLeftMenu() {
    var content = document.getElementById("left-menu-part");

    if (content.style.display == "none" || content.style.display == "") 
        content.style.display = "block";
    else 
        content.style.display = "none";
}


// 기수 버튼 누를 시 누른 버튼만 active 처리해주는 함수
function changeActive(id) {
    // 기수 버튼이 모두 같은 class로 묶여있는 상황
    // 해당 class='active' 모두 remove 하기
    document.querySelectorAll('.top-menu-button').forEach(function(button) {
        button.classList.remove('active');
    });

    // 파라미터로 받은 id 속성의 버튼만 class='active' 추가
    // 차후 css에서 active 속성을 가진 스타일을 가지게 됨
    var clickedButton = document.getElementById(id);
    clickedButton.classList.add('active');
}

// 기수 버튼 누를 시 왼쪽 메뉴에 맞춤형 컨텐츠 노출
function showContentLeftMenu(id, mainInitContentId) {
    // 왼쪽 메뉴에 표시될 컨텐츠가 같은 class로 묶여있는 상황
    // 해당 class를 모두 보이지 않게 none 처리
    var contents = document.getElementsByClassName('left-menu-container');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }

    // 파라미터로 받은 id 속성의 메뉴만 display함
    var selectedContent = document.getElementById(id);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }

    // 기수 별 메인 컨텐츠 초기화면 노출
    showContentMainPart(mainInitContentId)
}

// 왼쪽 레이아웃에서 세부메뉴 선택시 메인 컨텐츠 노출
function showContentMainPart(id) {

    // 세로모드일 때 왼쪽 메뉴 숨기기
    mediaQuery = window.matchMedia("(orientation: portrait)");
    if (mediaQuery.matches)
    {
        var menu = document.getElementById("left-menu-part");
        menu.style.display = "none";
    }

    // 모든 컨텐츠 보이지 않게 none 처리
    var contents = document.getElementsByClassName('main-content-init');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }

    var contents = document.getElementsByClassName('main-content-twitter');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }

    var contents = document.getElementsByClassName('main-content-search');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }

    var contents = document.getElementsByClassName('main-content-youtube');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';

        // main-content-youtube class에 iframe이 있는 경우 모두 제거
        iframe = contents[i].querySelector('iframe');
        if (iframe) 
            iframe.parentNode.removeChild(iframe);
    }

    var contents = document.getElementsByClassName('main-content-chzzk');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';

        // main-content-chzzk class에 iframe이 있는 경우 모두 제거
        iframe = contents[i].querySelector('iframe');
        if (iframe) 
            iframe.parentNode.removeChild(iframe);
    }

    // 파라미터로 받은 id 속성의 컨텐츠만 display함
    var selectedContent = document.getElementById(id);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }

    // 왼쪽 메뉴 버튼이 눌릴 때 ajax 호출 (파이썬 파일에서 처리됨)
    // 해당 버튼의 id가 click 되었는지 여부로 판단
    // 데이터를 받고 .html을 통해 특정 html 위치에 삽입
    // ` ` 문자로 html에 넣을 문장 삽입해야함 (작은 따옴표 아님)

    // 특정 요소가 클릭되었을 때 반응하려면 아래와 같이 추가
    //$(document).ready(function () {
        //$('.getVideoLink').click(function(){\
        //});
    //});

    // 유튜브 버튼 클릭
    if (id.includes("main-content-youtube"))
    {
        // Flask 서버에 동영상 데이터를 요청하는 AJAX 호출
        $.ajax({
            type: 'POST',
            url: '/get_video_data',
            success: function (data) {
                // 성공적으로 데이터를 받아왔을 때 처리
                const videoLink = data.video_link;
                const iframeCode = `<iframe src="${videoLink}" frameborder="0" allowfullscreen></iframe>`;
                $('#' + id + ' ' + '.video-container').html(iframeCode);
            },
            data: {
                member: id   
                // 다른 파라미터들도 필요하다면 여기에 추가
            },
            error: function () {
                // 오류 발생 시 처리
                $('#' + id).text('Error fetching data from Flask server.');
            }
        });
    }

    // 카페 버튼 클릭
    if (id.includes("main-content-search"))
    {
        // Flask 서버에서 데이터를 가져오는 동안 loading용 class만 노출
        $('#' + id + ' ' + '.search-background-loading').show()
        $('#' + id + ' ' + '.search-background').hide();
        //$('#' + id + ' ' + '.search-caution-container').hide();
        

        // Flask 서버에 데이터를 요청하는 AJAX 호출
        $.ajax({
            type: 'POST',
            url: '/get_search_data',
            success: function (data) {
                // 성공적으로 데이터를 받아왔을 때 처리
                var items = data;
                searchLink = data.search_link;
                var maxPost = 5;
                

                // 세로모드일 때 모바일 링크 제공하기
                mediaQuery = window.matchMedia("(orientation: portrait)");
                if (mediaQuery.matches)
                    searchLink = searchLink.replace(/(https:\/\/)([^.]+)(.+)/, "$1m.$2$3")

                member_name = id.split('-').pop()

                for (let i = 0; i < maxPost; ++i)
                {
                    document.querySelector('#' + id + ' ' + '#' + member_name + '-search-background-' + String(i)).onclick = function() {
                        window.open(items[i].link, '_blank');
                    };
                }
                
                for (let i = 0; i < maxPost; i++) 
                    $('#' + id + ' ' + '#' + member_name + '-search-title-' + String(i)).html(`${items[i].title}`);
                
                // Flask 서버에서 데이터를 가져온 후 loading용 class hide 처리, 가져온 데이터가 담긴 class 보여줌
                $('#' + id + ' ' + '.search-background').show()
                //$('#' + id + ' ' + '.search-caution-container').show();
                $('#' + id + ' ' + '.search-background-loading').hide()
                
            },
            data: {
                member: id   
                // 다른 파라미터들도 필요하다면 여기에 추가
            },
            error: function () {
                // 오류 발생 시 처리
                $('#' + id + ' ' + '.search-background-loading').hide()
                $('#' + id).text('Error fetching data from Flask server.');
            }
        });
    }

    // 방송 버튼 클릭
    if (id.includes("main-content-chzzk"))
    {
        channelId = "";
        parentLink = '127.0.0.1' // for local
        //parentLink = 'stelaika.onrender.com' // for pythonanywhere

        switch(id)
        {
            case 'main-content-chzzk-GangGi':
                channelId = 'rkdwl12';
                break;
            case 'main-content-chzzk-Kanna':
                channelId = 'airikanna_stellive';
                break;
            case 'main-content-chzzk-Yuni':
                channelId = 'ayatsunoyuni_stellive';
                break;
            case 'main-content-chzzk-Hina':
                channelId = 'shirayukihina_stellive';
                break;  
            case 'main-content-chzzk-Masiro':
                channelId = 'nenekomashiro_stellive';
                break;  
            case 'main-content-chzzk-Tabi':
                channelId = 'arahashitabi_stellive';
                break;
            case 'main-content-chzzk-Rize':
                channelId = 'akanelize_stellive';
                break;   
            default:
                break;  
        }

        // src channel에 트위치 스트리머 id 삽입
        // src parent에 embed될 사이트 주소 삽입 (port는 제거)
        const iframeCode = `<iframe src="https://player.twitch.tv/?channel=${channelId}&parent=${parentLink}" frameborder="0" allowfullscreen></iframe>`;
        $('#' + id + ' ' + '.broadcast-container').html(iframeCode);
    }
    
}

// 미디어 쿼리 리스너 함수
// css에서 미디어쿼리만으로 처리하면 javascript에서 동적으로 display = "none" 바뀐 이후 가로모드될 때 display = "block"으로 바뀌지 않아 처리
function handleMediaQueryChange(mq) {
    if (mq.matches) 
    {
        // 가로모드로 변경될 시 왼쪽 메뉴 표시
        var menu = document.getElementById("left-menu-part");
        menu.style.display = "block";
    }
    else
    {
        // 세로모드로 변경될 시 왼쪽 메뉴 가리기
        var menu = document.getElementById("left-menu-part");
        menu.style.display = "none";
    }

}

// 가로 모드를 감지하는 미디어 쿼리
var mediaQuery = window.matchMedia("(orientation: landscape)");

// 미디어 쿼리가 변경될 때 호출되는 함수 연결
mediaQuery.addListener(handleMediaQueryChange);

