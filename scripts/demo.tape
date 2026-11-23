# Record with scripts/demo.sh
Output docs/images/demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 760
Set Height 440
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 40ms

# The GIF does not show the version: the version of the branch is a dev version
Hide
Type `trakit() { command trakit "$@" | sed -E 's/^trakit .+ found: $/trakit found: /'; }`
Enter
Type "cd /tmp && export PS1='$ ' && clear"
Enter
Wait+Line@60s /^\$ *$/
Show

Sleep 500ms
Type 'trakit "Português (Brasil)"'
Sleep 500ms
Enter
Wait+Line@60s /^\$ *$/
Sleep 1500ms

Type 'trakit "British English (SDH) (PGS)"'
Sleep 500ms
Enter
Wait+Line@60s /^\$ *$/
Sleep 1500ms

Type 'trakit -t filename "movie.en.sdh.srt"'
Sleep 500ms
Enter
Wait+Line@60s /^\$ *$/
Sleep 7s
