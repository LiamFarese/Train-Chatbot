import { View, Text, StyleSheet, ScrollView, TextInput } from "react-native";
import { useTheme } from '@react-navigation/native';
import MessageBox from "../components/messageBox";

export default function Chat() {

    const colors = useTheme().colors;



    return (

        <View style={{

            flex: 1,
            backgroundColor: colors.background,
            
        }}>

            <View style={{

                backgroundColor: colors.card,
                flexDirection: 'row',
                justifyContent: 'center',
            }}>
                
            </View>

            <View style={{

                flex: 1
            }}>
                <ScrollView contentContainerStyle={{
                    
                    flex: 1,
                    alignSelf: 'center',
                    maxWidth: 720,
                    padding: 8,
                }}>

                    <MessageBox fill={true}>
                        Hello, la la la la la la la la la la la la la I am a very long message!{'\n'}{'\n'}
                        Is that okay?
                    </MessageBox>
                    <MessageBox>Calm down Good Sir!</MessageBox>
                    <MessageBox fill={true}>fine...</MessageBox>
                    
                </ScrollView>
            </View>

            <View style={{

                backgroundColor: colors.card,
                flexDirection: 'row',
                justifyContent: 'center',
            }}>
                <TextInput style={{
                    
                    flex: 1,
                    backgroundColor: '#fff',
                    maxWidth: 720,
            
                    borderColor: colors.border,
                    borderRadius: 26,
                    borderWidth: 2,
            
                    backgroundColor: colors.backgroundColor,

                    padding: 8,
                    paddingLeft: 16,
                    paddingRight: 16,
                    margin: 4,
                }}/>
            </View>
        </View>
    )
}
