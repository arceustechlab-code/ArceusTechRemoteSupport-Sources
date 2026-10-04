"""Test the actual outbound mapping module with isolated protobuf fixtures.
Native builds additionally compile it against the real generated protobuf types.
"""
from pathlib import Path
import subprocess

work = Path('work/mac-keyboard-tests')
work.mkdir(parents=True, exist_ok=True)
source = Path('client/src/support_keyboard.rs').resolve().as_posix()
fixtures = r'''
extern crate self as hbb_common;
pub mod protobuf {
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub struct EnumOrUnknown<T: Copy>(pub T);
    impl<T: Copy> EnumOrUnknown<T> {
        pub fn new(v: T) -> Self { Self(v) }
        pub fn enum_value_or_default(self) -> T { self.0 }
    }
}
pub mod protos { pub mod message {
    use crate::protobuf::EnumOrUnknown;
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub enum ControlKey { Meta, RWin, Control, RControl, Alt, RAlt, Shift, RShift }
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub enum KeyboardMode { Legacy, Map, Translate }
    pub mod key_event {
        use super::*;
        #[derive(Clone, Copy, Debug, PartialEq, Eq)]
        pub enum Union { ControlKey(EnumOrUnknown<super::ControlKey>), Chr(u32) }
    }
    #[derive(Clone, Debug, PartialEq, Eq)]
    pub struct KeyEvent {
        pub union: Option<key_event::Union>,
        pub mode: EnumOrUnknown<KeyboardMode>,
        pub modifiers: Vec<EnumOrUnknown<ControlKey>>,
        pub down: bool,
        pub press: bool,
    }
    impl KeyEvent {
        pub fn new() -> Self { Self {union: None, mode: EnumOrUnknown::new(KeyboardMode::Legacy), modifiers: vec![], down: false, press: false} }
        pub fn set_control_key(&mut self, key: ControlKey) {self.union=Some(key_event::Union::ControlKey(EnumOrUnknown::new(key)));}
        pub fn set_chr(&mut self, key: u32) {self.union=Some(key_event::Union::Chr(key));}
        pub fn chr(&self) -> u32 {match self.union {Some(key_event::Union::Chr(key)) => key, _ => 0}}
    }
    #[derive(Clone, Debug, PartialEq, Eq)]
    pub struct MouseEvent {pub modifiers: Vec<EnumOrUnknown<ControlKey>>}
}}
'''
tests = r'''
#[cfg(test)]
mod tests {
    use super::{support_keyboard::*, protos::message::*, protobuf::EnumOrUnknown};
    #[test]
    fn scope_and_manual_mapping() {
        for mac in [false,true] {for operator in [false,true] {
            for windows in [false,true] {for manual in [false,true] {
                assert_eq!(use_mac_windows_shortcuts(mac,operator,windows,manual), mac && operator && windows && !manual);
            }}
        }}
    }
    #[test]
    fn map_mode_press_release_and_repeat_for_both_command_keys() {
        for (source,target) in [(0xe05b,0x1d),(0xe05c,0xe01d)] {
            for (down,press) in [(true,false),(false,false),(false,true)] {
                let mut e=KeyEvent::new();
                e.mode=EnumOrUnknown::new(KeyboardMode::Map);
                e.set_chr(source); e.down=down; e.press=press;
                map_mac_windows_key(&mut e);
                assert_eq!(e.chr(),target);
                assert_eq!((e.down,e.press),(down,press));
            }
        }
    }
    #[test]
    fn command_shortcuts_keep_text_shift_alt_and_real_control() {
        for c in ['a','c','v','x','z','f','s','p','w','t','n','y','é','€'] {
            for mode in [KeyboardMode::Legacy,KeyboardMode::Map,KeyboardMode::Translate] {
                let mut e=KeyEvent::new(); e.set_chr(c as u32); e.mode=EnumOrUnknown::new(mode);
                e.modifiers=vec![ControlKey::Meta,ControlKey::RWin,ControlKey::Alt,ControlKey::Shift,ControlKey::Control,ControlKey::RControl]
                    .into_iter().map(EnumOrUnknown::new).collect();
                map_mac_windows_key(&mut e);
                assert_eq!(e.chr(),c as u32);
                assert_eq!(e.modifiers,vec![ControlKey::Control,ControlKey::RControl,ControlKey::Alt,ControlKey::Shift,ControlKey::Control,ControlKey::RControl]
                    .into_iter().map(EnumOrUnknown::new).collect::<Vec<_>>());
            }
        }
        // Unicode values that resemble physical codes must not be rewritten.
        let mut e=KeyEvent::new(); e.mode=EnumOrUnknown::new(KeyboardMode::Translate);
        e.set_chr(0xe05b); map_mac_windows_key(&mut e); assert_eq!(e.chr(),0xe05b);
    }
    #[test]
    fn legacy_modifier_keys_and_modified_mouse_clicks() {
        for (from,to) in [(ControlKey::Meta,ControlKey::Control),(ControlKey::RWin,ControlKey::RControl),
                         (ControlKey::Control,ControlKey::Control),(ControlKey::RControl,ControlKey::RControl),
                         (ControlKey::Alt,ControlKey::Alt),(ControlKey::Shift,ControlKey::Shift)] {
            for down in [false,true] {
                let mut e=KeyEvent::new(); e.set_control_key(from); e.down=down;
                map_mac_windows_key(&mut e);
                assert_eq!(e.union,Some(key_event::Union::ControlKey(EnumOrUnknown::new(to))));
                assert_eq!(e.down,down);
            }
        }
        let mut click=MouseEvent{modifiers:vec![EnumOrUnknown::new(ControlKey::Meta),EnumOrUnknown::new(ControlKey::Shift)]};
        map_mac_windows_mouse(&mut click);
        assert_eq!(click.modifiers,vec![EnumOrUnknown::new(ControlKey::Control),EnumOrUnknown::new(ControlKey::Shift)]);
    }
}
'''
main = work / 'main.rs'
main.write_text(fixtures + '\n#[path = "' + source + '"] mod support_keyboard;\n' + tests)
binary = work / 'mapping-tests'
subprocess.run(['rustc','--edition=2021','--test',str(main),'-o',str(binary)],check=True)
subprocess.run([str(binary)],check=True)
