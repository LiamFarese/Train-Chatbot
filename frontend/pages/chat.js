import { View, Text, ScrollView, FlatList, TextInput, Pressable, StatusBar } from "react-native";
import axios from 'axios';
import { useTheme } from '@react-navigation/native';
import MessageBlock from "../components/messageBlock";
import styles from '../styles';
import { useRef, useState, useEffect } from "react";
import Help from "./help";
import Button from "../components/button";

export default function Chat() {

    const [query, setQuery] = useState({
        message: null,
        current_query: null,
        departure: null,
        destination: null,
        time: null,
        date: null,
        return: null,
        return_time: null,
        return_date: null,
        history: []
    })

    const colors = useTheme().colors;

    // States //

    // const [youAreLastSender, setYouAreLastSender] = useState(false)
    const [currentTyping, setCurrentTyping] = useState(null)
    const [currentModal, setCurrentModal] = useState(null);

    // alternates between 'owner' and 'you', owner being first
    const [messages, setMessages] = useState([]);
    

    // References //

    const textInput = useRef()
    const scrollView = useRef()

    // Functions //

    // Load greeting message upon loading
    useEffect(() => {
        const getHello = () => {
            try {
                axios.get('http://localhost:8000/user/hello')
                .then((res) => {
                    //console.log(res.data);
                    setMessages([res.data.message]);
                });
                
            } catch (error) {
                console.error("Error fetching hello", error);
            };
        };
        getHello();
    }, []);

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

    // for submitting the message to the chatbot
    // edit when this functionality has been added
    const submitMessage = async () => {
        console.log(currentTyping)
        // close function if message is invalid
        if (currentTyping == null || currentTyping == ''
            || currentTyping == undefined) return

        textInput.current.clear()
        textInput.current.focus()

        newMessages = [...messages]

        const updatedQuery = {
            ...query,
            message: currentTyping
        };

        newMessages.push([currentTyping])
        setMessages(newMessages)

        console.log(updatedQuery)

        // add code here //
        try {
            const response = await axios.post('http://localhost:8000/send-chat/', updatedQuery);
            newMessages.push([response.data.message])
            setMessages(newMessages)
            setQuery(prevQuery => ({
                ...prevQuery,
                ...response.data
            }));
            console.log(response.data)
            console.log(query)
        } catch (error) {
            console.error('Error sending message:', error);
        };
        setCurrentTyping(null)

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