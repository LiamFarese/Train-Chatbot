import { View, Text, ScrollView, TextInput, Pressable, StatusBar } from "react-native";
import { useTheme } from '@react-navigation/native';
import MessageBlock from "../components/messageBlock";
import styles from '../styles';
import { useRef, useState } from "react";

export default function Chat() {


    // States //

    const colors = useTheme().colors;
    const [youAreLastSender, setYouAreLastSender] = useState(true)
    const [currentTyping, setCurrentTyping] = useState("")
    // alternates between 'owner' and 'you', owner being first
    const [messages, setMessages] = useState([

        [
            "Hello, la la la la la la la la la la la la la I am a very long message!",
            "do you even care?",
        ],

        [
            "not really mate",
            "not really...",
        ],
    ]);


    // References //

    textInput = useRef()


    // Functions //

    function getMessageBlocks(messages)
    {
        messageBlocks = []
        key = 0
        you = false;

        messages.forEach((message) => {
    
            messageBlocks.push(
                
                <MessageBlock 

                    left={!you} 
                    key={'messageBlock' + key++}
                    owner={you ? 'You' : 'Chatbot'}
                    messages={message}
                />
            )

            you = !you
        })

        return messageBlocks
    }

    function submitMessage() {

        if (currentTyping == undefined) return
        if (currentTyping == '') return

        textInput.current.clear()
        textInput.current.blur()

        newMessages = [...messages]

        if (youAreLastSender) {

            newMessages[newMessages.length - 1].push(currentTyping)
        }
        else {
        
            newMessages.push([message])
            setYouAreLastSender(true)
        }

        return newMessages
    }

    return (

        <View style={{

            flex: 1,
            backgroundColor: colors.background,
        }}>
            <StatusBar/>


            {/* Top Header */}

            <View style={[styles(colors).header]}>

                <View style={[
                    
                    styles(colors).headerFooterInner,
                    styles(colors).maxWidth,
                {
                    justifyContent: 'flex-end',
                }]}>
                    <Text style={[

                        styles(colors).text,
                        styles(colors).title,
                    {
                        flex: 1,
                        margin: 4,
                    }]}>
                        
                        Train Chatbot
                    </Text>

                    <Pressable style={[

                        styles(colors).container,
                    {
                        alignItems: 'center',
                    }]}
                    >
                        <Text style={[styles(colors).text,]}>About</Text>

                    </Pressable>

                    <View style={{marginRight: 4}}/>

                    <Pressable style={[

                        styles(colors).container,
                        styles(colors).primary,
                    {
                        alignItems: 'center',
                    }]}
                    >
                        <Text style={[

                            styles(colors).text,
                        {
                            color: colors.card
                        }]}>
                            Help

                        </Text>
                    </Pressable>
                </View>
            </View>

            
            {/* Messages */}

            <View style={{

                flex: 1,
            }}>
                <ScrollView contentContainerStyle={[
                    
                    styles(colors).maxWidth,
                {
                    flex: 1,
                    padding: 8,
                    justifyContent: 'flex-end',
                }]}>
                    {getMessageBlocks(messages)}

                </ScrollView>
            </View>
            

            {/* Footer (text box and send button) */}

            <View style={[

                styles(colors).footer,
            {
                marginTop: 16,
            }]}>
                <View style={[
                    
                    styles(colors).headerFooterInner,
                    styles(colors).maxWidth,
                ]}>
                    <TextInput style={[

                        styles(colors).container,
                        styles(colors).text,
                    {
                        alignItems: 'center',
                        flex: 1,
                    }]}
                        placeholder={'Type message here...'}
                        onChangeText={newText => setCurrentTyping(newText)}
                        ref={textInput}
                        onSubmitEditing={() => setMessages(submitMessage())}
                    />

                    <View style={{marginRight: 4}}/>

                    <Pressable style={[

                        styles(colors).container,
                        styles(colors).primary,
                    {
                        alignItems: 'center',
                    }]}
                        onPress={() => 
                            {
                                if (currentTyping != undefined)
                                {
                                    setMessages(submitMessage())
                                }
                            }}
                    >
                        <Text style={[

                            styles(colors).text,
                        {
                            color: colors.card
                        }]}>
                            Send

                        </Text>
                    </Pressable>
                </View>
            </View>
        </View>
    )
}
