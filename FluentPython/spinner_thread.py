import threading
import itertools
import time
import sys

class Signal:
    # 외부에서 스레드를 제어하기 위해 사용할 go 속성 하나만 있는 간단한 가변 객체 정의
    go = True
    
def spin(msg, signal):
    # 별도의 스레드에서 실행되는 함수
    # signal 인수는 바로 앞에서 정의한 Signal 클래스의 객체를 받음
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        # itertools.cycle()은 주어진 시퀀스를 순환하면서 끝없이 항목을 생성하므로,
        # 이 for문은 무한 루프가 된다.
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))  # 텍스트 모드 애니메이션 기법. 문자열의 길이만큼 백스페이스를 반복해서 커서를 앞으로 이동
        time.sleep(.1)
        if not signal.go:
            # go 속성이 True가 아니라면 루프를 빠져나온다.
            break
    write(' ' * len(status) + '\x08' * len(status))
    # 공백 문자로 덮어쓰고 다시 커서를 처음으로 이동해서 메시지 출력 행을 청소한다
    
def slow_function():
    # 시간이 오래걸리는 함수라고 가정
    time.sleep(3)
    # 주 스레드에서 sleep() 함수를 호출할 때 GIL이 해제되므로 두번째 스레드가 진행
    return 42

def supervisor():
    # 두번째 스레드를 만들고, 스레드 객체를 출력하고, 시간이 오래 걸리는 연산을 수행 후 스레드 제거
    signal = Signal()
    spinner = threading.Thread(target=spin, args=('thinking!', signal))
    print('spinner object: ', spinner)  # 두번째 스레드 객체 출력
    spinner.start()  # 두번째 스레드 실행
    result = slow_function()  # slow_function() 함수를 실행. 주 스레드 블로킹, 두번째 스레드의 애니메이션 시작
    signal.go = False  # signal의 상태를 변경. spin() 함수 안의 for 루프가 중단 됨
    spinner.join()  # spinner 스레드가 끝날 때까지 기다린다
    return result

def main():
    result = supervisor()  # supervisor() 함수 실행
    print('Answer: ', result)
if __name__ == "__main__":
    main()
        
