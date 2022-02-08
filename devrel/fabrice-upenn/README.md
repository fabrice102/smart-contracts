# Smart contract examples for course at UPenn (2022)

**WARNING**: Smart contracts in this repo are just to illustrate some properties of Algorand smart contracts.
They have not been audited and must not be used as is in any production environment.

Before everything, set:

```
export SB="path/to/sandbox/script"
```

## Demo: State example

Very simple example with one global state variable counter.

1. Create the app: `./state_create.sh`
2. Check the global state: `./state_print_global.sh`
3. Call the app: `./state_call.sh` (a few times)
4. Check the global state: `./state_print_global.sh`
5. Show how to debug: `./state_debug.sh` (open Chrome, open the Developer Tools inside, go to the URL printed)
6. Delete the app: `./clean.sh`

## Demo: Simple escrow

1. Run: `python3 simple_escrow_demo.py`
2. Possibility to debug using: `./simple_escrow_debug.sh`

## Snippets

`snippets.py` is used to generate the PyTeal / TEAL snippets in the slides


