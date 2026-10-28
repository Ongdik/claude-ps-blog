# [백준 1920] 수 찾기 - 리스트 in에서 set으로

## 문제

- 출처: [백준 1920](https://www.acmicpc.net/problem/1920)
- N개의 정수가 주어지고, 다음으로 주어지는 M개의 수가 각각 그 안에 있으면 1, 없으면 0을 출력한다.
- N과 M은 최대 100,000이다.

## 처음 풀이: 리스트에 넣고 in으로 확인

읽자마자 그냥 리스트에 넣고 `in`으로 있는지 보면 되겠다고 생각했다.

```python
n = int(input())
cards = list(map(int, input().split()))
m = int(input())
for x in map(int, input().split()):
    print(1 if x in cards else 0)
```

예제는 다 맞았는데 제출하니까 시간 초과가 났다.

## in 한 줄이 왜 느린지 몰랐던 부분

코드에 반복문이 하나밖에 없어서 왜 느린지 감이 안 왔다. 그래서 `in`이 내부에서 어떻게 동작하는지 물어봤다.

리스트에서 `in`은 앞에서부터 하나씩 비교한다고 한다. 찾는 수가 없으면 끝까지 다 본다. 결국 눈에 보이는 반복문은 하나지만, `in` 안에 반복문이 하나 더 숨어 있었던 거다.

그럼 한 번에 찾는 방법은 없는지 이어서 물어봤고, `set`은 해시로 위치를 바로 계산해서 리스트처럼 하나씩 비교하지 않는다는 걸 알게 됐다.

## set으로 바꿔서 다시 제출

바꾼 건 `cards`를 만드는 한 줄이다. 출력도 한 줄씩 `print`하지 않고 모아서 한 번에 했다.

```python
import sys
input = sys.stdin.readline

n = int(input())
cards = set(map(int, input().split()))
m = int(input())
out = []
for x in map(int, input().split()):
    out.append("1" if x in cards else "0")
print("\n".join(out))
```

이번에는 통과했다.

## 돌아보며

리스트 `in`이 느리다는 얘기는 어디서 들어본 것 같은데, 막상 코드를 쓸 때는 전혀 떠오르지 않았다. 반복문이 하나라서 괜찮다고 생각했던 게 컸다.

다음부터는 같은 자료에서 여러 번 찾는 코드가 보이면 `in` 앞에 있는 게 리스트인지 먼저 확인해 볼 생각이다.
