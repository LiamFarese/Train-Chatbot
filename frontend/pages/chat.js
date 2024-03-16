import { View, Text, ScrollView, TextInput, Pressable, Dimensions } from "react-native";
import { useTheme } from '@react-navigation/native';
import MessageBlock from "../components/messageBlock";
import styles from '../styles';

export default function Chat() {

    const colors = useTheme().colors;

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
                    <MessageBlock
                    
                        messages={[

                            "Hello, la la la la la la la la la la la la la I am a very long message!",
                            "do you even care?"
                        ]}

                        left={true}
                        owner={'Chatbot'}
                    />
                    
                    <MessageBlock
                    
                        messages={[

                            "not really mate",
                            "not really..."
                        ]}

                        owner={'You'}
                    />
                    
                    <MessageBlock
                    
                        messages={[

                            "You're so mean! :("
                        ]}

                        left={true}
                        owner={'Chatbot'}
                    />
                </ScrollView>
            </View>

            <View style={[

                styles(colors).header,
            {

            }]}>
                <View style={[
                    
                    styles(colors).headerInner,
                    styles(colors).maxWidth,
                ]}>
                    <TextInput style={[

                        styles(colors).container,
                    {
                        alignItems: 'center',
                        flex: 1,
                    }]}/>

                    <View style={{marginRight: 4}}/>

                    <Pressable style={[

                        styles(colors).container,
                        styles(colors).primary,
                    {
                        alignItems: 'center',
                    }]}>
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
