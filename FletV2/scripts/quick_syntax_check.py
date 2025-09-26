from pathlib import Path


def main():
    files = [
        Path('views/dashboard.py'),
    ]
    errs = 0
    for f in files:
        try:
            src = f.read_bytes()
            compile(src, str(f), 'exec')
            print(f'OK: {f}')
        except Exception as e:
            print(f'ERR: {f}: {e}')
            errs += 1
    print('DONE with', errs, 'errors')
    return errs

if __name__ == '__main__':
    raise SystemExit(main())
