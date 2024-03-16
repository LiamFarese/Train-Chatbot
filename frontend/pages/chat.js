import { View, Text, ScrollView, TextInput, Pressable, Dimensions } from "react-native";
import { useTheme } from '@react-navigation/native';
import MessageBlock from "../components/messageBlock";
import styles from '../styles';
import { useState } from "react";

export default function Chat() {

    const colors = useTheme().colors;

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

        [
            "You're so mean! :(",
        ]
    ]);

    const [youAreLastSender, setYouAreLastSender] = useState(false)
    const [currentTyping, setCurrentTyping] = useState("")

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
                    owner={you ? 'you' : 'owner'}
                    messages={message}
                />
            )

            you = !you
        })

        return messageBlocks
    }

    function submitMessage(message) {

        newMessages = messages

        if (youAreLastSender) {

            newMessages[newMessages.length - 1].push(message)
            console.log(newMessages)
        }
        else {

            newMessages.push([message])
            setYouAreLastSender(true)
        }

        setMessages(newMessages)
    }

    return (

        <View style={{

            flex: 1,
            backgroundColor: colors.background,
        }}>
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

            <View style={[

                styles(colors).header,
            {
                marginTop: 16,
            }]}>
                <View style={[
                    
                    styles(colors).headerInner,
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
                                submitMessage(currentTyping)
                                this.textInput.clear()
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
