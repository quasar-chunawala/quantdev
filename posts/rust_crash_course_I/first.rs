#[derive(Debug)]
pub enum List{
    Empty,
    Element(i32, Box<List>),
}

pub fn main(){
    let list : List = List::Element(1, Box::new(List::Element(2, Box::new(List::Empty))));
    println!("{list:?}");
}