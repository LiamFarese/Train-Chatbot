import { Modal, Pressable, ScrollView, Text, View } from "react-native";
import styles from "../styles";
import { useTheme } from "@react-navigation/native";
import helpText from "./helpText";


/*
props:

    - visible
    - onClose
*/

export default function Help(props) {

    const colors = useTheme().colors;

    return (

        <Modal
            transparent={true}
            visible={props.visible}
            animationType={"fade"}

            style={{

            }}
        >
            <View style={{

                flex: 1,
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
            }}>

                <Pressable style={{

                    height: 72,
                }}
                    onPress={props.onClose}
                />

                <View

                    style={[{

                        flex: 1,
                        padding: 16,
                },
                    styles(colors).maxWidth,
                    styles(colors).modal,
                ]}
                >
                    {/* Header */}

                    <View

                        style={{

                            flexDirection: 'row',
                            justifyContent: 'space-between',
                            paddingBottom: 12,
                        }}
                    >
                        <Text style={[

                            styles(colors).text,
                            styles(colors).title,
                        {
                            paddingTop: 8,
                        }]}>
                            Help
                        
                        </Text>
                        
                        <Pressable style={[

                            styles(colors).container,
                        {
                            alignSelf: 'flex-end'
                        }]}
                            onPress={props.onClose}
                        >
                            <Text style={styles(colors).text}>Close</Text>

                        </Pressable>
                    </View>
                    
                    {/* Main Text */}
                    <View style={styles(colors).scrollViewContainer}>
                        <ScrollView>
                            <Text style={styles(colors).text}>{helpText}</Text>
                        </ScrollView>
                    </View>
                </View>
            </View>
        </Modal>
    )
}
