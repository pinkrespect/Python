import asyncio
import itertools
import sys

@asyncio.coroutine  # asyncio에 사용할 코루틴은 @asyncio.coroutine으로 데코레이트 해야함(권장)
def spin(msg):
    # spin() 함수에서 스레드를 종료하기 위해 사용했던 signal 인수가 필요 없음
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write(('\x08') * len(status))
        try:
            yield from asyncio.sleep(.1)
            # 이벤트 루프를 블로킹하지 않고 잠자기 위해 time.sleep(.1) 대신 사용
        except asyncio.CancelledError:
            break
    write(' ' * len(status) + '\x08' * len(status))
    
@asyncio.coroutine
def slow_function():
    # 코루틴이 잠자면서 입출력을 수행하는 체 하는 동안 이벤트 루프가 진행될 수 있게 하기 위해서 yield from을 사용
    # 입출력을 위해 장시간 기다리는 것처럼 보이게 만듬
    yield from asyncio.sleep(3)
    return 42

@asyncio.coroutine
def supervisor():
    # supervisor()도 코루틴이므로, yield from을 이용해서 slow_function()을 구동할 수 있다.
    spinner = asyncio.async(spin('Thinking!'))  # spin() 코루틴의 실행을 스케쥴링하고 Task 객체 않에 넣어, Task 객체를 즉시 반환한다.
    print('spinner object: ', spinner)  # Task 객체 출력
    result = yield from slow_function()  # slow_function() 구동 후 값을 받아온다. 이벤트 루프는 계속 실행 중이다.
    spinner.cancel()  # Task 객체는 cancel() 메소드를 호출해서 취소할 수 있다. 예외를 잡아서 지연시키거나 취소 요청을 거부할 수 있다.
    return result

def main():
    loop = asyncio.get_event_loop()  # 이벤트 루프에 대한 참조 가져오기
    result = loop.run_until_complete(supervisor())
    loop.close()
    print('Answer:', result)
    
if __name__ == '__main__':
    main()
