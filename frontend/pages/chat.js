import { View, Text, ScrollView, FlatList, TextInput, Pressable, StatusBar } from "react-native";
import axios from 'axios';
import { useTheme } from '@react-navigation/native';
import MessageBlock from "../components/messageBlock";
import styles from '../styles';
import { useEffect, useRef, useState } from "react";
import Help from "./help";
import Button from "../components/button";

export default function Chat() {

    const colors = useTheme().colors;

    // States //

    // const [youAreLastSender, setYouAreLastSender] = useState(false)
    const [currentTyping, setCurrentTyping] = useState(null)
    const [currentModal, setCurrentModal] = useState(null);
    const [socket, setSocket] = useState(null);

    // alternates between 'owner' and 'you', owner being first
    const [messages, setMessages] = useState([

        // [
        //     "Hello, la la la la la la la la la la la la la I am a very long message!",
        //     "do you even care?",
        // ],

        // [
        //     "not really mate",
        //     "not really...",
        // ],

        // [
        //     "goblin",
        //     "goblin",
        //     "goblin",
        //     "goblin",
        //     "goblin",
        //     "goblin",
        //     "goblin",
        //     "goblin",
        // ],

        // [
        //     "what's wrong with you?!"
        // ],
    ]);
    

    // References //

    const textInput = useRef();
    const scrollView = useRef();


    useEffect(() => {
        var ws = new WebSocket("ws://127.0.0.1:8000/ws");
        
        ws.onopen = () => {
            console.log("Connected to WebSocket")
        }
        
        ws.onmessage = (event) => {
            console.log(event.data)
            setMessages((previous_messages) => {
                console.log(previous_messages)
                return [...previous_messages, event.data];
            });
            console.log(messages)
        };
        
        ws.onerror = (error) => {
            console.log(`WebSocket error: ${error}`);
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    

    // Functions //

    function getMessageBlocks(messages)
    {
        messageBlocks = []
        key = 0
        you = true;

        messages.forEach((message) => {

            //console.log(message)
    
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

    // for submitting the message to the chatbot
    // edit when this functionality has been added
    const submitMessage = async () => {
        
        // close function if message is invalid
        if (currentTyping == null || currentTyping == ''
            || currentTyping == undefined) return

        textInput.current.clear()
        textInput.current.focus()

        newMessages = [...messages]

        newMessages.push(currentTyping)
        setMessages(newMessages)


        // add code here //
        // try {
        //     const response = await axios.post('http://localhost:8000/user/send-chat/', {
        //       currentTyping,
        //     });
        //     console.log(response)
        //     newMessages.push([response.data.message])
        //     setMessages(newMessages)
        // } catch (error) {
        //     console.error('Error sending message:', error);
        // };
        
        
        socket.send(currentTyping);
        setCurrentTyping(null);

    }

    return (

        <View style={{

            flex: 1,
            backgroundColor: colors.background,
        }}>
            <StatusBar/>

            {/* Modals */}

            <Help
                visible={currentModal == 'Help'}
                onClose={() => {setCurrentModal(null)}}
            />


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


                    {/* About Button */}

                    <Button

                        onPress={() => setCurrentModal('Help')}
                        primary={true}
                    >
                        Help

                    </Button>
                </View>
            </View>

            
            {/* Messages */}

            <ScrollView contentContainerStyle={[
                
                styles(colors).maxWidth,
            {
                padding: 8,
                paddingBottom: 32,
                justifyContent: 'flex-end',
            }]}
                ref={ref => {this.scrollView = ref}}
                onContentSizeChange={() => this.scrollView.scrollToEnd()}
            >
                {getMessageBlocks(messages)}

            </ScrollView>

            <View style={{paddingBottom: 32,}}/>
            

            {/* Footer (text box and send button) */}

            <View style={[
                
                styles(colors).headerFooterInner,
                styles(colors).maxWidth,
            {
                position: 'absolute',
                bottom: 0,
                padding: 8,
            }]}>
                <TextInput style={[

                    styles(colors).container,
                    styles(colors).text,
                {
                    alignItems: 'center',
                    flex: 1,
                }]}
                    ref={textInput}
                    placeholder={'Type message here...'}
                    onChangeText={newText => setCurrentTyping(newText)}
                    onTouchStart={() => this.scrollView.scrollToEnd() }
                    onSubmitEditing={() => submitMessage()}
                    placeholderTextColor={colors.text}
                />

                <View style={{marginRight: 2,}} />

                <Button 

                    primary={true}
                    onPress={() => submitMessage()}
                >
                    <Text style={[

                        styles(colors).text,
                    {
                        color: 'white'
                    }]}>
                        Send

                    </Text>
                </Button>
            </View>
        </View>
    )
}
