# 1. 깃 초기화 (이미 했다면 생략 가능하지만 해도 상관없음)
git init
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git branch -M main

# 2. 방금 만든 GitHub 주소 연결하기 (주소 부분에 복사한 걸 붙여넣으세요!)
git remote add origin https://github.com/본인아이디/저장소이름.git

# 3. 현재 코드들을 장바구니에 담기
git add .

# 4. 포장하기 (이름표 붙이기)
git commit -m "첫 번째 업로드"

# 5. 가지 이름 정리 (오류 방지용)
git branch -M main

# 6. GitHub로 발사!
git push -u origin main 
## 여기서 잠깐 -u 옵션과 -f 옵션의 차이 
### 만약 readme.md와 같은 파일이 있고 없을때 애러 날수 있음 
###  ! [rejected]        main -> main (fetch first)
### error: failed to push some refs to 'https://github.com/EmmettHwang/GwangsangWebAPP.git'

## 이때에 -f 옵션을 사용함. 

### git init에서 한글 문제로 애러 날때 사용
> chcp 65001   
> git init   
> git config --global core.quotepath false   