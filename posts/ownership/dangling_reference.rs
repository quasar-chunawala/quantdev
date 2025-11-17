fn as_str(data: &u32) -> &str{
    // Compute the string
    let s = format!("{}", data);

    // Oh No! We returned a reference to something that
    // only exists in this function.
    // Dangling reference! Alas!
    return &s;
}

pub fn main(){
    let x : u32 = 42;
    as_str(&x);
}