# [백준 1920] 수 찾기 - 정렬과 이분 탐색

## 문제 소개

- 출처: [백준 1920](https://www.acmicpc.net/problem/1920)
- N개의 정수가 주어지고, 다음으로 주어지는 M개의 수가 각각 그 안에 있는지 확인한다.
- N과 M은 최대 100,000이다.

## 문제 접근 과정

수 하나를 찾을 때마다 배열 전체를 훑으면 최악의 경우 100,000 × 100,000 = 10^10번 비교한다. 탐색 한 번의 비용을 O(N)보다 줄여야 한다.

같은 배열에서 여러 번 찾으므로, 배열을 한 번 정렬해 두면 탐색마다 **이분 탐색**을 쓸 수 있다.

## 풀이 방법

### 정렬 후 범위 좁히기

정렬된 배열의 가운데 값과 찾는 수를 비교해서, 찾는 수가 더 작으면 왼쪽 절반, 크면 오른쪽 절반만 남긴다. 한 번 비교할 때마다 범위가 절반으로 줄어든다.

## 코드

```python
import sys
input = sys.stdin.readline

n = int(input())
arr = sorted(map(int, input().split()))
m = int(input())

out = []
for x in map(int, input().split()):
    lo, hi = 0, n - 1
    found = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == x:
            found = 1
            break
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    out.append(str(found))
print("\n".join(out))
```

`input`을 `sys.stdin.readline`으로 바꾼 것은 입력 줄이 길어서다.

## 시간복잡도와 공간복잡도

정렬에 O(N log N), M개의 수를 각각 이분 탐색하는 데 O(M log N)이 든다. 전체는 O((N + M) log N)이고, N = M = 100,000이면 약 340만 번 연산이다. 공간은 입력 배열을 저장하는 O(N)이다.

## 정리

- 입력 크기가 10^5이고 질의도 10^5개면, 질의 하나를 O(N)으로 처리하는 방법은 쓸 수 없다.
- 같은 배열에서 여러 번 탐색하면 정렬 비용을 한 번 내고 탐색마다 O(log N)으로 줄일 수 있다.

<!-- 이미지 삽입 위치: 이분 탐색 범위가 줄어드는 그림 -->
